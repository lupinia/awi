#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.text import slugify

from datetime import timedelta
from mptt.models import MPTTModel, TreeForeignKey

from awi.utils.text import format_html, summarize
from awi_access.models import access_control

def viewtype_options():
	blocks_map = settings.DEERTREES_BLOCK_MAP
	viewtypes = []
	for map_name, map in blocks_map.iteritems():
		if map.get('meta',{}).get('option_name',False) and map.get('meta',{}).get('selectable',True):
			viewtypes.append((map_name, map.get('meta',{}).get('option_name',map_name),))
	return viewtypes

@python_2_unicode_compatible
class category(MPTTModel, access_control):
	CONTENT_SUMMARY_CHOICES = (
		('misc', 'Miscellaneous'),
		('image', 'Images/Photos'),
		('page', 'Writing'),
		('link', 'External Links'),
	)
	
	title = models.CharField(max_length=60)
	slug = models.SlugField()
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
	summary = models.CharField(max_length=255, null=True, blank=True)
	desc = models.TextField(null=True, blank=True, verbose_name='description body text')
	
	view_type = models.CharField(choices=viewtype_options(), max_length=15, default='default', help_text='Determines the placement of content when this category is displayed.')
	sitemap_include = models.BooleanField(default=True, verbose_name='include in sitemap', help_text='Check this box to include this category in sitemap views.')
	trash = models.BooleanField(default=False, db_index=True, verbose_name='recycle bin', help_text='System field:  Indicates whether this category is the "recycle bin" for deleted items.')
	
	background_tag = models.ForeignKey('sunset.background_tag', null=True, blank=True, on_delete=models.SET_NULL, help_text='Set this to indicate the preferred background image themes for this category.')
	icon = models.ForeignKey('sunset.image_asset', null=True, blank=True, on_delete=models.SET_NULL, help_text='System field:  Image asset used as a thumbnail for this category.')
	icon_manual = models.BooleanField(default=False, db_index=True, help_text='System field:  Indicates whether the Icon field was set manually; if so, it will not be replaced by the automatic thumbnail assignment script.')
	content_summary = models.CharField(max_length=20, default='misc', choices=CONTENT_SUMMARY_CHOICES, help_text='System field:  Stores the main content type for this category, used to display an icon when no image asset is selected.  Will be set by the automatic thumbnail assignment script.')
	always_fresh = models.BooleanField(default=False, blank=True, help_text='If checked, the "old content" note will not be added to older content in this category. Useful for things like policy directories.')
	
	cached_url = models.CharField(max_length=255, null=True, blank=True, unique=True, help_text='System field:  Full unique slug for this category, including all parents.')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def __str__(self):
		return self.title
	
	def get_absolute_url(self):
		return reverse('category', kwargs={'cached_url':self.cached_url,})
	
	@property
	def display_title(self):
		return self.title
	
	@property
	def content_summary_choices_simplified(self):
		choices_simplified = []
		for choice in self.CONTENT_SUMMARY_CHOICES:
			choices_simplified.append(choice[0])
		return choices_simplified
	
	def set_content_summary(self, summary='misc'):
		if summary != self.content_summary:
			choices_simplified = self.content_summary_choices_simplified
			
			if summary in choices_simplified:
				self.content_summary = summary
				self.save()
			else:
				if self.content_summary != 'misc':
					self.content_summary = 'misc'
					self.save()
		
		return self.content_summary
	
	@property
	def body_html(self):
		if self.desc:
			return format_html(self.desc)
		else:
			return format_html(self.summary)
	
	@property
	def icon_url(self):
		if self.icon:
			return self.icon.get_url()
		elif self.mature:
			return "%simages/icons/mature128.png" % settings.STATIC_URL
		else:
			return "%simages/icons/default-category-%s-128.png" % (settings.STATIC_URL, self.content_summary)
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.desc, summary=self.summary, length=length, prefer_long=True)
		else:
			return summarize(body=self.desc, summary=self.summary, length=length)
	
	@property
	def summary_short(self):
		return self.get_summary()
	
	@property
	def summary_long(self):
		return self.get_summary(512)
	
	# ALIAS
	@property
	def rss_description(self):
		return self.summary_short
	
	def save(self, *args, **kwargs):
		if self.parent:
			self.cached_url = '%s/%s' % (self.parent.cached_url, self.slug)
		else:
			self.cached_url = self.slug
		super(category, self).save(*args, **kwargs)
	
	def can_edit(self, request=False):
		if not request:
			return (False,'access_norequest')
		else:
			canview = self.can_view(request)
			if not canview[0]:
				return canview
			else:
				return super(category, self).can_edit(request, perm_check='deertrees.change_category')
	
	class MPTTMeta:
		order_insertion_by = ['title']
	
	class Meta:
		verbose_name_plural = 'categories'

@python_2_unicode_compatible
class tag(models.Model):
	title = models.CharField(max_length=200,null=True,blank=True)
	slug = models.SlugField(max_length=200,unique=True)
	desc = models.TextField(null=True,blank=True)
	
	view_type = models.CharField(choices=viewtype_options(), max_length=15, default='default', help_text='Determines the placement of content when this tag is displayed.')
	sitemap_include = models.BooleanField(default=True, verbose_name='include in sitemap', help_text='Check this box to include this tag in sitemap views.')
	public = models.BooleanField(default=True, blank=True, db_index=True)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	@property
	def display_title(self):
		if self.title:
			return self.title
		else:
			return self.slug
	
	def __str__(self):
		return self.display_title
	
	def get_absolute_url(self):
		return reverse('tag', kwargs={'slug':self.slug,})
	
	def can_edit(self, request=False):
		if not request:
			return (False,'access_norequest')
		else:
			return (request.user.has_perm('deertrees.change_tag'), 'access_perms')
	
	def can_view(self, request=False):
		if self.public:
			return (True, '')
		else:
			if request:
				if request.user.is_superuser:
					return (True, '')
				else:
					return (False, 'access_404')
			else:
				return (False, 'access_norequest')
	
	def is_public(self):
		return self.public
	
	@property
	def synonym_list(self):
		sluglist = []
		if self.title:
			# Why did I write this check?  What problem was I trying to solve?
			# Is this even what I intended?  Or was this a mistake?
			sluglist.append(self.slug)
		
		synonyms = self.synonyms.all().values_list('slug', flat=True)
		if synonyms:
			sluglist += list(synonyms)
		
		return sluglist
	
	@property
	def body_html(self):
		return format_html(self.desc)
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.desc, length=length, prefer_long=True, fallback='')
		else:
			return summarize(body=self.desc, length=length, fallback='')
	
	@property
	def summary_short(self):
		return self.get_summary()
	
	@property
	def summary_long(self):
		return self.get_summary(512)
	
	# ALIAS
	@property
	def rss_description(self):
		return self.summary_short
	
	def add_synonym(self, new_synonym):
		new_synonym = slugify(new_synonym)
		duplicate_check = tag_synonym.objects.filter(slug=new_synonym)
		if duplicate_check:
			if duplicate_check.first().parent == self:
				return True
			else:
				return False
		else:
			tag_synonym.objects.create(slug=new_synonym, parent=self)
			return True
	
	def merge(self, target):
		"""
		tag.merge(target) -> (success, reason)
		Merge target tag into this tag, keeping all relationships for both.
		sitemap_include will be set to True if it's True for either tag. 
		Oldest timestamp_post value will be kept.
		Only this tag's value for slug will be kept, intended use is to simplify overlaps.
		NOTE:  Object provided as target parameter will be deleted!
		
		Returns a tuple:
			success: Boolean, indicates whether the merge succeeded
			reason:  String, provides a reason for failure if success is False
		"""
		success = False
		reason = ''
		if type(self) != type(target):
			success = False
			reason = 'object type mismatch'
		else:
			# Check whether it already exists
			duplicate_check = tag_synonym.objects.filter(slug=target.slug)
			synonym_exists = False
			if duplicate_check:
				duplicate = duplicate_check.first()
				if duplicate.parent != self:
					success = False
					reason = 'target is synonym of: %s' % duplicate.parent.slug
				else:
					synonym_exists = True
			
			# Rectify field differences
			if target.timestamp_post < self.timestamp_post:
				# Use the oldest timestamp
				self.timestamp_post = target.timestamp_post
			
			if self.view_type == 'default' and target.view_type != 'default':
				# If the target has a manual view type, apply it here.
				self.view_type = target.view_type
			
			self.sitemap_include = any([self.sitemap_include, target.sitemap_include])
			
			if target.desc:
				if self.desc:
					self.desc = '%s\n\nDescription from %s:\n%s' % (self.desc, target.slug, target.desc)
				else:
					self.desc = target.desc
			
			if target.title:
				if self.title:
					if self.title != target.title:
						if self.desc:
							self.desc = 'aka %s\n%s' % (target.title, self.desc)
						else:
							self.desc = 'aka %s' % target.title
				else:
					self.title = target.title
			
			# Time to merge!
			# Make sure all items tagged with target are also tagged with self
			self.leaves.add(*target.leaves.all())
			target.synonyms.all().update(parent=self)
			if not synonym_exists:
				self.add_synonym(target.slug)
			
			self.save()
			target.delete()
			success = True
		
		return (success, reason)
	
	class Meta:
		ordering = ['slug',]

@python_2_unicode_compatible
class tag_synonym(models.Model):
	parent = models.ForeignKey(tag, on_delete=models.CASCADE, related_name='synonyms')
	slug = models.SlugField(max_length=200,unique=True)
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def get_absolute_url(self):
		return reverse('tag', kwargs={'slug':self.parent.slug,})
	
	def __str__(self):
		return self.slug
	
	class Meta:
		ordering = ['slug',]

@python_2_unicode_compatible
class external_link_type(models.Model):
	name = models.CharField(max_length=200, verbose_name='site name')
	label = models.CharField(max_length=200, verbose_name='link label')
	icon = models.ImageField(upload_to='linkicons_ext', null=True, blank=True)
	url_format = models.CharField(max_length=250, blank=True, null=True, verbose_name='URL format', help_text='Use &lt;id&gt; to create a placeholder for remote_id on links of this type.')
	
	featured = models.BooleanField(db_index=True, blank=True, default=False)
	public = models.BooleanField(db_index=True, blank=True, default=True)
	notes = models.TextField(null=True, blank=True)
	sites = models.ManyToManyField(Site, db_index=True, help_text='Sites/domains on which this item will appear.')
	
	def __str__(self):
		return self.name
	
	@property
	def icon_url(self):
		if self.icon:
			return "%s%s" % (settings.MEDIA_URL,self.icon.name)
		else:
			return "%simages/icons/default-link-32.png" % settings.STATIC_URL
	
	class Meta:
		verbose_name = 'external platform'

@python_2_unicode_compatible
class external_link(models.Model):
	link_type = models.ForeignKey(external_link_type, on_delete=models.CASCADE, related_name='links', verbose_name='platform')
	parent = models.ForeignKey('leaf', on_delete=models.CASCADE, related_name='external_links')
	full_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='URL')
	remote_id = models.CharField(max_length=250, blank=True, null=True, verbose_name='remote object ID')
	label_override = models.CharField(max_length=250, blank=True, null=True, verbose_name='label override')
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	published = models.BooleanField(db_index=True, blank=True, default=False)
	automated = models.BooleanField(db_index=True, blank=True, default=False)
	notes = models.TextField(null=True, blank=True)
	
	def __str__(self):
		return '%s: %s' % (self.link_type.name, unicode(self.parent)) # type: ignore
	
	def get_absolute_url(self):
		return self.url
	
	@property
	def url(self):
		if self.full_url:
			return self.full_url
		elif self.remote_id and self.link_type.url_format:
			return self.link_type.url_format.replace('<id>', self.remote_id)
		else:
			return ''
	
	@property
	def label(self):
		if self.label_override:
			return self.label_override
		else:
			return self.link_type.label
	
	def clean(self):
		if not self.full_url and not self.remote_id:
			raise ValidationError('Either a full URL or a remote ID are required.')
		if not self.link_type.url_format and not self.full_url:
			raise ValidationError('A full URL is required for this link type')
		return super(external_link,self).clean()
	
	class Meta:
		verbose_name = 'external platform link'
		ordering = ['-link_type__featured']


#	This model has been modified for the Awi website, and requires the Awi Access app
#	This is a single categorized node; everything else that belongs to a category should extend this class
@python_2_unicode_compatible
class leaf(access_control):
	TIMEDISP_OPTIONS = (('post','Posted'),('mod','Modified'))
	
	author_override = models.CharField(max_length=100, null=True, blank=True, help_text="If this was written by a guest author, enter their name here.  Enter 'none' to hide the author info from display (only use this for things like system directories and site policies where authorship is irrelevant).")
	
	basename = models.SlugField(max_length=127)
	cat = models.ForeignKey(category, null=True, blank=True, on_delete=models.PROTECT, verbose_name='category', related_name='leaves')
	tags = models.ManyToManyField(tag, blank=True, related_name='leaves')
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created', help_text='Set this to a future date to schedule it.')
	timedisp = models.CharField(max_length=10, choices=TIMEDISP_OPTIONS, default='post', verbose_name='preferred timestamp', help_text='Determines which timestamp (modified, or created) will be publicly displayed.  The other option will only be visible to users who can edit this item.')
	
	type = models.CharField(max_length=20, default='unknown', db_index=True, help_text='System field:  Indicates which model this leaf is.')
	
	def __str__(self):
		return '%s:  %d' % (self.type.capitalize(), self.pk)
	
	# An extension of get_absolute_url() to include the domain
	def get_complete_url(self, request=None):
		if request:
			domain = request.get_host()
		else:
			primary_site = self.sites.all().order_by('pk').first()
			if not primary_site:
				primary_site = Site.objects.get(pk=settings.SITE_ID)
			
			domain = primary_site.domain
			if 'www' not in domain:
				domain = 'www.%s' % domain
		
		return 'https://%s%s' % (domain, self.get_absolute_url())
	
	def save(self, *args, **kwargs):
		if not self.pk:
			self.type = self.__class__.__name__
		super(leaf, self).save(*args, **kwargs)
	
	def scheduled(self):
		if self.published and self.timestamp_post > timezone.now():
			return True
		else:
			return False
	
	def can_view(self, request=False):
		public_check = self.is_public()
		if public_check[0]:
			return (True, '')
		else:
			canview = super(leaf, self).can_view(request)
			if canview[0] and self.scheduled() and (self.owner != request.user or not request.user.has_perm('deertrees.change_leaf')):
				canview = (False,'access_404')		# If it's scheduled, and we don't have elevated privileges, it doesn't exist.
			
			return canview
	
	def can_edit(self, request=False):
		if not request:
			return (False,'access_norequest')
		else:
			canview = self.can_view(request)
			if not canview[0]:
				return canview
			else:
				return super(leaf, self).can_edit(request, perm_check='deertrees.change_leaf')
	
	def is_public(self):
		public, restrictions = super(leaf, self).is_public()
		if self.scheduled():
			public = False
			restrictions.append('Scheduled future postdate')
		
		return (public, restrictions)
	
	# Helper method for extracting a reason for non-public status that's easier to work with programmaticly
	@property
	def restriction(self):
		cur_restriction = super(leaf, self).restriction
		if self.scheduled() and not self.is_public()[0]:
			return 'scheduled'
		else:
			return cur_restriction
	
	def tag_item(self, taglist):
		return_data = {'skipped':[], 'added':[], 'created':[]}
		if ', ' in taglist:
			new_tags = taglist.split(', ')
		elif ',' in taglist:
			new_tags = taglist.split(',')
		else:
			new_tags = [taglist,]
		
		old_tags = {}
		cur_tags = self.tags.all()
		if cur_tags:
			for old_tag in cur_tags:
				old_tags[old_tag.slug] = old_tag
		
		new_tag_objs = []
		for new_tag in new_tags:
			if old_tags.get(new_tag, False):
				return_data['skipped'].append(new_tag)
			else:
				new_tag = slugify(new_tag)
				new_tag_obj = tag.objects.get_or_create(slug=new_tag)
				new_tag_objs.append(new_tag_obj[0])
				if new_tag_obj[1]:
					return_data['created'].append(new_tag)
				else:
					return_data['added'].append(new_tag)
		
		if new_tag_objs:
			self.tags.add(*new_tag_objs)
		
		return return_data
	
	def display_times(self):
		return_times = [{},{}]
		if self.timedisp == 'post':
			return_mod = 1
			return_post = 0
		else:
			return_mod = 0
			return_post = 1
		
		return_times[return_post]['timestamp'] = self.timestamp_post
		return_times[return_mod]['timestamp'] = self.timestamp_mod
		return_times[return_post]['label'] = 'Posted'
		return_times[return_mod]['label'] = 'Updated'
		
		return return_times
	
	def get_links(self, request=False):
		link_query = self.external_links.select_related('link_type')
		if request:
			if self.can_edit(request)[0]:
				return link_query.all()
			elif request.user.is_authenticated():
				return link_query.filter(link_type__sites__id=settings.SITE_ID, published=True)
		
		return link_query.filter(link_type__sites__id=settings.SITE_ID, published=True, link_type__public=True)
	
	@property
	def timestamp(self):
		if self.timedisp == 'post':
			return self.timestamp_post
		else:
			return self.timestamp_mod
	
	@property
	def rss_description(self):
		return 'No Description'
	
	@property
	def is_recent(self):
		if self.timestamp > (timezone.now() - timedelta(days=30*6)):
			return True
		else:
			return False
	
	@property
	def admin_owned(self):
		if self.owner.pk == settings.SITE_OWNER_ACCOUNT_ID and not self.author_override:
			return True
		else:
			return False
	
	@property
	def is_old(self):
		if self.cat.always_fresh or not self.admin_owned:
			return False
		else:
			if self.timestamp_mod < (timezone.now() - timedelta(days=365*10)):
				return True
			elif (self.timestamp_post < (timezone.now() - timedelta(days=365*10))) and (self.timestamp_mod < (timezone.now() - timedelta(days=365*2))):
				return True
			else:
				return False
	
	@property
	def author(self):
		if self.author_override:
			if self.author_override.lower() == 'none':
				return ''
			else:
				return self.author_override
		else:
			if self.owner.get_full_name():
				return self.owner.get_full_name()
			else:
				return self.owner.get_username()
	
	@property
	def tags_list(self):
		return self.tags.filter(public=True).values_list('slug', flat=True)
	
	class Meta:
		unique_together = ('basename', 'cat')


#	Create a leaf that links to something else that isn't part of this category system.
#	Handy for things like third-party apps, or self-contained apps with their own organizational structure.
@python_2_unicode_compatible
class special_feature(leaf):
	url = models.CharField(max_length=60, unique=True, verbose_name='URL', help_text='Similar to a Slug field, but can accept any character, to make it easier to link to non-DeerTrees URLs.')
	url_reverse = models.CharField(max_length=250, null=True, blank=True, help_text='Enter the keyword used by Django to look up this special feature in urls.py.')
	title = models.CharField(max_length=60)
	desc = models.CharField(max_length=255, null=True, blank=True, verbose_name='Description')
	directory = models.BooleanField(blank=True, default=True, help_text='Does this link to content that behaves like a single file, or like a subdirectory?')
	
	def get_absolute_url(self):
		return '%s%s' % (reverse('category', kwargs={'cached_url':self.cat.cached_url,}), self.url)
	
	def __str__(self):
		return '%s: %s' % (self.emulation_mode.capitalize(), self.title)
	
	def save(self, *args, **kwargs):
		if not self.basename:
			self.basename = slugify(self.url)
			if leaf.objects.filter(cat=self.cat, basename=self.basename).exists():
				self.basename = '%s%d' % (self.basename, special_feature.objects.all().count()+1)
		super(special_feature, self).save(*args, **kwargs)
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.desc, length=length, prefer_long=True)
		else:
			return summarize(body=self.desc, length=length)
	
	@property
	def emulation_mode(self):
		if self.directory:
			return 'path'
		else:
			return 'file'
	
	@property
	def summary_short(self):
		return self.get_summary()
	
	@property
	def summary_long(self):
		return self.get_summary(512)
	
	# ALIAS
	@property
	def rss_description(self):
		return self.summary_short
	
	class Meta:
		verbose_name = 'special feature'
