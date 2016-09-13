#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import exiftool
import os
import urllib

from django.db import models
from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify

from datetime import datetime
from fractions import Fraction
from PIL import Image, ImageOps

from awi_access.models import access_control
from deertrees.models import leaf, category, tag
from sunset.utils import *

def image_asset_uploadto(instance, filename):
	original = filename.split('.')
	return 'gallery/%s_%s.%s' % (instance.parent.slug, instance.type, original[-1])

class background_tag(models.Model):
	tag = models.CharField(max_length=50)
	default = models.BooleanField(default=False, blank=True)
	def __unicode__(self):
		return self.tag

class image(leaf):
	# Map EXIF/IPTC keys to attributes on this model.
	# All others will be created as image_meta objects.
	META_MAP = {
		'Composite:DateTimeCreated':'timestamp_post', 
		'Composite:GPSLatitude':'geo_lat', 
		'Composite:GPSLongitude':'geo_long', 
		'EXIF:ImageDescription':'body', 
		'IPTC:Caption-Abstract':'body', 
		'IPTC:Keywords':'tags', 
		'IPTC:ObjectName':'title', 
		'XMP:Description':'body', 
		'XMP:Subject':'tags', 
		'XMP:Title':'title', 
	}
	
	slug=models.SlugField(unique=True)
	title=models.CharField(max_length=100,null=True,blank=True)
	body = models.TextField(null=True,blank=True)
	summary = models.CharField(max_length=255,null=True,blank=True)
	rebuild_assets = models.BooleanField(default=True)	# If true, asset files will be rebuilt on next run.
	auto_fields = models.BooleanField(default=True)		# If true, fields listed in META_MAP will be overwritten from EXIF data.
	is_new = models.BooleanField(default=True)			# If true, set published=True after first asset build.
	
	geo_lat = models.DecimalField(decimal_places = 15, max_digits = 20, blank=True, null=True)
	geo_long = models.DecimalField(decimal_places = 15, max_digits = 20, blank=True, null=True)
	
	# Page backgrounds
	bg_tags=models.ManyToManyField(background_tag, blank=True)
	
	# Attributes used only on this classes's methods.
	PIL_obj = False
	orig_path = False
	orig_type = False
	
	def __unicode__(self):
		if self.title:
			return self.title
		else:
			return self.slug
	
	def save(self, *args, **kwargs):
		if self.body and not self.summary:
			body_text = strip_tags(self.body)
			if len(body_text) < 255:
				self.summary = body_text
				self.body = None
			else:
				self.summary = body_text[:250].rsplit(' ',1)[0]+'...'
		super(image, self).save(*args, **kwargs)
	
	def get_absolute_url(self):
		return reverse('image_single', kwargs={'cached_url':self.cat.cached_url, 'slug':self.slug})
	
	# Download a copy of this image's original asset to a working directory.
	# Set return_PIL_obj=True to get a PIL object.
	# Returns a file path otherwise.
	def get_working_original(self, return_PIL_obj=False):
		if self.orig_path:
			# We already did this, so just send back what we already opened.
			if return_PIL_obj:
				if self.PIL_obj:
					return self.PIL_obj
				else:
					self.PIL_obj = Image.open(self.orig_path)
					return self.PIL_obj
			else:
				return self.orig_path
		else:
			orig_asset_check = self.assets.filter(type='original')
			if orig_asset_check:
				orig_asset = orig_asset_check.first()
				# Parse the original's name to get the actual filename, and the filetype extension.
				dest_name = orig_asset.image_file.name.split('/')
				img_filetype_raw = orig_asset.image_file.name.split('.')
				self.orig_type = img_filetype_raw[-1]
				
				# Download original to working directory
				asset_dl = urllib.urlretrieve(orig_asset.get_url(), '%s/%s' % (settings.SUNSET_CACHE_DIR, dest_name[-1]))
				imgfile_check = open(asset_dl[0])
				imgfile_check.close()
				import_log.objects.create(command='image.get_working_original', message='Successfully downloaded original', image=self)
				
				if return_PIL_obj:
					self.PIL_obj = Image.open(asset_dl[0])
					import_log.objects.create(command='image.get_working_original', message='Successfully opened original with Pillow', image=self)
					return self.PIL_obj
				else:
					self.orig_path = asset_dl[0]
					return self.orig_path
			else:
				import_log.objects.create(command='image.get_working_original', message='Unable to download or open original image', image=self)
				return False
	
	# Parse this image's original asset for metadata, and save it to the database.
	def build_meta(self):
		img_path = self.get_working_original()
		if img_path:
			metareader = exiftool.ExifTool('/usr/local/bin/exiftool')
			metareader.start()
			if metareader.running:
				meta = metareader.get_metadata(img_path)
				metareader.terminate()
				
				# If a meta value for this image exists with this key, update it.
				# Otherwise, create a new one.
				# And if this is a special key, update the self image object.
				# Let's start by setting up some containers for new data
				new_self_attrs = {}
				new_meta_objs = []
				meta_keys = {}
				
				# Now let's grab all the existing meta keys, to save some database queries.
				if not meta_keys:
					meta_keys_q = image_meta_key.objects.all()
					for key_obj in meta_keys_q:
						meta_keys[key_obj.key] = key_obj
				
				for key, value in meta.iteritems():
					# Get or create a meta key object for this key.
					cur_key = meta_keys.get(key, False)
					if not cur_key:
						cur_key = image_meta_key.objects.create(key=key)
						meta_keys[key] = cur_key
					
					if not cur_key.ignore:
						# Check whether this is a special key.
						if self.auto_fields and self.META_MAP.get(key,False):
							new_self_attrs[self.META_MAP[key]] = value
						
						# Check whether we already have this meta value in the database for this image.
						meta_check = self.meta.filter(key=cur_key)
						if meta_check.exists():
							cur_meta = meta_check.first()
							if not cur_meta.manual_entry:
								cur_meta.data = value
								cur_meta.save()
						else:
							new_meta_objs.append(image_meta(image=self, key=cur_key, data=value))
				
				# Done with this loop!  Time to clean up a bit.
				if new_meta_objs:
					image_meta.objects.bulk_create(new_meta_objs)
					import_log.objects.create(command='image.build_meta', message='Successfully created %d new meta entries' % len(new_meta_objs), image=self)
				if self.auto_fields and new_self_attrs:
					for attr, value in new_self_attrs.iteritems():
						if attr == 'tags':
							# Special case:  Bulk-create tags
							new_tags = ','.join(map(str, value))
							tag_status = self.tag_item(new_tags)
						else:
							if attr == 'timestamp_post':
								# Special case:  Timestamp
								# Trying to parse datetimes from ExifTool is a horrendous mess, because the format could be almost anything.
								if '-' in value:
									timestamp, tzstamp = value.split('-')
								elif '+' in value:
									timestamp, tzstamp = value.split('+')
								else:
									timestamp = value
									tzstamp = ''
								date_obj = datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
								value = timezone.make_aware(date_obj)
							setattr(self, attr, value)
					self.save()
					import_log.objects.create(command='image.build_meta', message='Successfully set %d new meta entries' % len(new_self_attrs), image=self)
				
				# Done!
				return True
			else:
				import_log.objects.create(command='image.build_meta', message='Unable to start ExifTool', image=self)
				return False
		else:
			import_log.objects.create(command='image.build_meta', message='Original image asset unavailable', image=self)
			return False
	
	def build_resize(self, type):
		if settings.SUNSET_IMAGE_ASSET_SIZES.get(type,False):
			params = {}
			type_params = settings.SUNSET_IMAGE_ASSET_SIZES[type]
			original = self.get_working_original(True)
			if original.format == 'JPEG':
				params['quality'] = 100
			
			if type_params.get('watermark',False):
				# Watermark this image before performing operations.
				working_copy = watermark(original)
			else:
				working_copy = original.copy()
			
			if type_params.get('exact',False):
				working_copy = ImageOps.fit(working_copy, type_params.get('size',(100,100)), Image.LANCZOS, centering=(0.5,0.5))
			else:
				if working_copy.width < type_params.get('size',(100,100))[0] and working_copy.height < type_params.get('size',(100,100))[1]:
					# We're already within the right size, so just use the original.
					pass
				else:
					working_copy.thumbnail(type_params.get('size',(100,100)), Image.LANCZOS)
			
			working_copy.save(fp='%s/%s_%s.%s' % (settings.SUNSET_CACHE_DIR, self.slug, type, self.orig_type), **params)
			
			# Save new image to database
			img_obj = File(open('%s/%s_%s.%s' % (settings.SUNSET_CACHE_DIR, self.slug, type, self.orig_type),'rb'))
			
			asset_check = self.assets.filter(type=type)
			if asset_check.exists():
				asset = asset_check.first()
				# If we already have an asset, replace its image file with this one.
				asset.image_file.delete()
				asset.image_file.save('%s_%s.%s' % (self.slug, type, self.orig_type), img_obj)
				asset.save()
				import_log.objects.create(command='image.build_resize', message='Successfully updated asset %d' % asset.pk, image=self)
			else:
				new_asset = image_asset(type=type, parent=self)
				new_asset.image_file.save('%s_%s.%s' % (self.slug, type, self.orig_type), img_obj)
				new_asset.save()
				import_log.objects.create(command='image.build_resize', message='Successfully created new asset %d' % new_asset.pk, image=self)
			
			# Time to clean up after ourselves.
			img_obj.close()
			os.remove('%s/%s_%s.%s' % (settings.SUNSET_CACHE_DIR, self.slug, type, self.orig_type))
			import_log.objects.create(command='image.build_resize', message='File cleanup complete for %s asset.' % type, image=self)
			return True
		else:
			import_log.objects.create(command='image.build_resize', message='Invalid size:  %s' % type, image=self)
			return False
	
	def build_assets(self):
		success = []
		if self.rebuild_assets:
			for type in settings.SUNSET_IMAGE_ASSET_SIZES:
				self.build_resize(type)
				success.append(type)
			
			if success and self.is_new:
				self.is_new = False
				self.rebuild_assets = False
				self.published = True
				self.save()
				import_log.objects.create(command='image.build_assets', message='Successfully built assets (%s) and marked image as published.' % ', '.join(success), image=self)
			elif success:
				self.rebuild_assets = False
				self.save()
				import_log.objects.create(command='image.build_assets', message='Successfully rebuilt assets (%s)' % ', '.join(success), image=self)
			else:
				import_log.objects.create(command='image.build_assets', message='Unable to build assets.', image=self)
			
			return success
		else:
			import_log.objects.create(command='image.build_assets', message='Image not marked for asset rebuild.', image=self)
			return False

class image_asset(models.Model):
	TYPE_OPTIONS=(
		('original','Original Upload'),
		('icon','Icon'),
		('display','Display-Resized Copy'),
		('full','Public Full-Size Image'),
		('bg','Site Background'),
		('unknown','Unknown')
	)
	
	type=models.CharField(max_length=16,choices=TYPE_OPTIONS,default='unknown')
	parent=models.ForeignKey(image, related_name='assets')
	img_width=models.IntegerField(null=True,blank=True)
	img_height=models.IntegerField(null=True,blank=True)
	timestamp_post=models.DateTimeField(auto_now_add=True)
	timestamp_mod=models.DateTimeField(auto_now=True)
	image_file=models.ImageField(upload_to=image_asset_uploadto, height_field='img_height', width_field='img_width')
	hash = models.CharField(max_length=255, null=True, blank=True)
	
	def __unicode__(self):
		return self.image_file.name
	
	def get_url(self):
		return "%s%s" % (settings.MEDIA_URL,self.image_file.name)
	
	def save(self, *args, **kwargs):
		self.hash = hash_file(self.image_file)
		if self.type == 'original':
			self.parent.rebuild_assets = True
			self.parent.save()
		super(image_asset, self).save(*args, **kwargs)

class image_meta_key(models.Model):
	FORMAT_OPTIONS = (
		('text','Plain Text'),
		('url','URL (url|label)'),
		('datetime','Date/Time'),
		('fraction','Fraction'),
		('aperture','Aperture'),
		('flash','Flash'),
		('focallength','Focal Length (in millimeters)'),
		('exposuremode','Exposure Mode (Auto/Manual)'),
		('exposureprogram','Exposure Program (Auto/Program/Tv/Av)'),
		('meteringmode','Metering Mode (Spot/Center-Weighted)'),
		('automan','Auto/Manual Binary Choice'),
	)
	
	key=models.CharField(max_length=100, unique=True)
	display_name=models.CharField(max_length=100,blank=True,null=True)
	format_type=models.CharField(max_length=40,choices=FORMAT_OPTIONS,default='text')
	public=models.BooleanField(default=False)
	ignore=models.BooleanField(default=False)
	
	def __unicode__(self):
		if self.display_name:
			return self.display_name
		else:
			return self.key
	
	def format(self, data):
		func = getattr(self, 'format_%s' % self.format_type, 'format_text')
		return func(data)
	
	def format_text(self, data):
		return data
	
	def format_url(self, data):
		if '|' in data:
			url, label = data.split('|')
		else:
			url = data
			url_raw = data.replace('https://', '')
			url_raw = url_raw.replace('http://', '')
			url_raw = url_raw.rstrip('/')
			if '/' in url_raw:
				url_parts = url_raw.split('/')
				label = '%s/.../%s' % (url_parts[0],url_parts[-1])
			else:
				label = url_raw
		
		return '<a href="%s">%s</a>' % (url,label)
	
	def format_aperture(self, data):
		return ('f%f' % float(data)).rstrip('0').rstrip('.')
	
	def format_focallength(self, data):
		return '%dmm' % float(data)
	
	def format_datetime(self, data):
		# Trying to parse datetimes from ExifTool is a horrendous mess, because the format could be almost anything.
		if '-' in data:
			timestamp, tzstamp = data.split('-')
		elif '+' in data:
			timestamp, tzstamp = data.split('+')
		else:
			timestamp = data
			tzstamp = ''
		date_obj = datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
		return datetime.strftime(date_obj, '%b %d, %Y %H:%M')
	
	def format_fraction(self, data):
		fraction_obj = Fraction(float(data)).limit_denominator(8000)
		return str(fraction_obj)
	
	def format_flash(self, data):
		flash_settings = {
			0:'No Flash', 
			1:'Fired',
			5:'Fired, Return Not Detected',
			7:'Fired, Return Detected',
			8:'On, Did Not Fire',
			9:'On, Fired',
			13:'On, Return Not Detected',
			15:'On, Return Detected',
			16:'Off, Did Not Fire',
			20:'Off, Did Not Fire, Return Not Detected',
			24:'Auto, Did Not Fire',
			25:'Auto, Fired',
			29:'Auto, Fired, Return Not Detected',
			31:'Auto, Fired, Return Detected',
			32:'No Flash Function',
			48:'Off, No Flash Function',
			65:'Fired, Red-Eye Reduction',
			69:'Fired, Red-Eye Reduction, Return Not Detected',
			71:'Fired, Red-Eye Reduction, Return Detected',
			73:'On, Red-Eye Reduction',
			77:'On, Red-Eye Reduction, Return Not Detected',
			79:'On, Red-Eye Reduction, Return Detected',
			80:'Off, Red-Eye Reduction',
			88:'Auto, Did Not Fire, Red-Eye Reduction',
			89:'Auto, Fired, Red-Eye Reduction',
			93:'Auto, Fired, Red-Eye Reduction, Return Not Detected',
			95:'Auto, Fired, Red-Eye Reduction, Return Detected',
		}
		return flash_settings.get(int(data), 'Unknown')
	
	def format_exposureprogram(self, data):
		exposure_settings = {
			0:'Unknown', 
			1:'Manual',
			2:'Program AE (Semi-Auto)',
			3:'Aperture-Priority AE (Semi-Auto)',
			4:'Shutter-Priority AE (Semi-Auto)',
			5:'Creative (Slow Speed)',
			6:'Action (High Speed)',
			7:'Portrait',
			8:'Landscape',
			9:'Bulb',
		}
		return exposure_settings.get(int(data), 'Unknown')
	
	def format_exposuremode(self, data):
		exposure_settings = {
			0:'Auto', 
			1:'Manual',
			2:'Manual Bracket',
		}
		return exposure_settings.get(int(data), 'Unknown')
	
	def format_automan(self, data):
		choices = {
			0:'Auto', 
			1:'Manual',
		}
		return choices.get(int(data), 'Unknown')
	
	def format_meteringmode(self, data):
		meter_settings = {
			0:'Unknown', 
			1:'Average',
			2:'Center-Weighted Average',
			3:'Spot',
			4:'Multi-Spot',
			5:'Multi-Segment',
			6:'Partial',
			255:'Other',
		}
		return meter_settings.get(int(data), 'Unknown')
	
	class Meta:
		ordering = ['display_name']

class image_meta(models.Model):
	key = models.ForeignKey(image_meta_key)
	image = models.ForeignKey(image, related_name='meta')
	data = models.TextField(blank=True)
	manual_entry = models.BooleanField(default=False, help_text="Check this box to prevent this meta tag from being overwritten by data embedded in the image file.")
	
	def __unicode__(self):
		return u'%s - %s: %s' % (self.image, self.key, unicode(self.data))
	
	def format_data(self):
		return self.key.format(self.data)

class batch_import(access_control):
	folder = models.FilePathField(path=settings.SUNSET_IMPORT_DIR, recursive=True, allow_files=False, allow_folders=True)
	cat = models.ForeignKey(category, help_text="This must be set manually.")
	next_sequence_number = models.IntegerField(blank=True, default=1)
	timestamp_mod=models.DateTimeField(auto_now=True)
	timestamp_post=models.DateTimeField(default=timezone.now)
	timestamp_sync=models.DateTimeField(blank=True,null=True)
	active = models.BooleanField(default=True)
	sync_success = models.BooleanField(default=False)
	
	# The following fields will auto-populate discovered images, in addition to standard data from parsing the original file, if set.
	tags = models.ManyToManyField(tag, blank=True, help_text="Added to tags embedded in file, if set.")
	title = models.CharField(max_length=60, null=True, blank=True, help_text="Overrides title embedded in file, if set.  Defaults to null if empty.  Use &lt;seq&gt; to insert a sequential number.")
	slug = models.SlugField(null=True, blank=True, help_text="Overrides slug, if set.  Defaults to filename if empty.  Use &lt;seq&gt; to insert a sequential number.")
	desc = models.TextField(null=True, blank=True, help_text="Overrides description embedded in file, if set.")
	
	def folder_shortname(self):
		return self.folder.replace(settings.SUNSET_IMPORT_DIR, '')
	
	def __unicode__(self):
		return self.folder_shortname()
	
	def check_folder(self):
		if not self.active:
			import_log.objects.create(command='batch_import.check_folder', message='Unable to perform sync on inactive batch.', batch=self)
			return False
		
		contents = os.listdir(self.folder)
		if contents:
			return contents
		else:
			import_log.objects.create(command='batch_import.check_folder', message='Unable to retrieve directory listing, or directory is empty.', batch=self)
			return False
	
	def process_folder(self):
		if not self.active:
			import_log.objects.create(command='batch_import.process_folder', message='Unable to perform sync on inactive batch.', batch=self)
			return False
		
		self.sync_success=False
		self.save()
		
		success_count = 0
		file_list = self.check_folder()
		if file_list:
			existing_check = self.images.all()
			existing = {}
			if existing_check.exists():
				for existing_obj in existing_check:
					existing[existing_obj.img_filename] = existing_obj
			
			self_sites = self.sites.all()
			self_tags = self.tags.all()
			self_meta = self.meta.all()
			for img_filename in file_list:
				if os.path.isdir('%s/%s' % (self.folder, img_filename)):
					continue
				
				img_PIL_obj = Image.open('%s/%s' % (self.folder, img_filename))
				img_filename_raw = img_filename.split('.')
				img_filename_type = img_filename_raw.pop()
				img_file_slug = '.'.join(img_filename_raw)
				img_PIL_obj.close()
				img_file_obj = File(open('%s/%s' % (self.folder, img_filename),'rb'))
				
				img_hash = hash_file(img_file_obj)
				
				if existing.get(img_filename,False):
					cur_img = existing.get(img_filename,False)
					cur_img_orig_check = cur_img.img_obj.assets.filter(type='original')
					if cur_img_orig_check.exists:
						asset = cur_img_orig_check.first()
						if asset.hash != img_hash:
							asset.image_file.delete()
							asset.image_file.save('%s_original.%s' % (cur_img.img_obj.slug, img_filename_type), img_file_obj)
							asset.save()
							cur_img.save()
							success_count = success_count + 1
							import_log.objects.create(command='batch_import.process_folder', message='Updated existing image with new version of file.', batch=self, image=cur_img.img_obj)
				else:
					new_img = image(
						cat=self.cat,
						timedisp='post',
						published=False,
						featured=False,
						mature=self.mature,
						security=self.security,
						owner=self.owner,
					)
					
					if self.title:
						if '<seq>' in self.title:
							cur_title = self.title.replace('<seq>', str(self.next_sequence_number))
						else:
							cur_title = self.title
						new_img.title = cur_title
						new_img.auto_fields = False
					else:
						new_img.title = img_file_slug
					
					if self.slug:
						if '<seq>' in self.slug:
							cur_slug = self.slug.replace('<seq>', str(self.next_sequence_number))
						else:
							cur_slug = self.slug
						new_img.slug = cur_slug
					else:
						new_img.slug = slugify(img_file_slug)
					
					exist_check = image.objects.filter(slug=new_img.slug)
					if exist_check.exists():
						new_img.slug = '%s-%d' % (new_img.slug, self.next_sequence_number)
					
					if self.desc:
						new_img.body = self.desc
					
					# At this point, we've populated all of our required fields.
					# Time to set up the meta and assets
					new_img.save()
					
					if self_sites:
						new_img.sites.add(*self_sites)
					
					if self_tags:
						new_img.tags.add(*self_tags)
					
					if self_meta:
						for meta in self_meta:
							image_meta.objects.create(key=meta.key, image=new_img, data=meta.data, manual_entry=True)
					
					new_asset = image_asset(type='original', parent=new_img)
					new_asset.image_file.save('%s_original.%s' % (new_img.slug, img_filename_type), img_file_obj)
					new_asset.save()
					
					batch_image.objects.create(parent=self, img_filename=img_filename, img_obj=new_img, hash=img_hash)
					self.next_sequence_number = self.next_sequence_number + 1
					self.save()
					success_count = success_count + 1
					import_log.objects.create(command='batch_import.process_folder', message='Successfully created new image.', batch=self, image=new_img)
			
			self.timestamp_sync = timezone.now()
			self.sync_success=True
			self.save()
			return success_count
		else:
			self.sync_success=True
			self.save()
			import_log.objects.create(command='batch_import.process_folder', message='batch_import.check_folder() returned False; nothing to do.', batch=self)
			return False

class batch_meta(models.Model):
	key=models.ForeignKey(image_meta_key)
	parent=models.ForeignKey(batch_import, related_name='meta')
	data=models.TextField(blank=True, help_text="Added to file meta; overrides data already in file, in the event of a conflict.")
	
	def __unicode__(self):
		return '%s - %s: %s' % (self.parent, self.key, unicode(self.data))

class batch_image(models.Model):
	parent = models.ForeignKey(batch_import, related_name='images')
	img_filename = models.CharField(max_length=255)
	img_obj = models.ForeignKey(image, null=True, blank=True)
	timestamp_mod = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=255, null=True, blank=True)
	hash = models.CharField(max_length=255, null=True, blank=True)
	
	def __unicode__(self):
		return '%s - %s' % (unicode(self.parent), self.img_filename)

class import_log(models.Model):
	CMD_OPTIONS = (
		('manage.process_images','process_images (management command)'),
		('image.get_working_original','image.get_working_original'),
		('image.build_meta','image.build_meta'),
		('image.build_resize','image.build_resize'),
		('image.build_assets','image.build_assets'),
		('batch_import.check_folder','batch_import.check_folder'),
		('batch_import.process_folder','batch_import.process_folder'),
	)
	
	command = models.CharField(max_length=50, choices=CMD_OPTIONS)
	timestamp = models.DateTimeField(auto_now_add=True)
	message = models.TextField()
	image = models.ForeignKey(image,blank=True,null=True)
	batch = models.ForeignKey(batch_import,blank=True,null=True)