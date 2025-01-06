#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions and helpers

from django.apps import apps
from django.conf import settings

from deerfind.models import g2map, g2raw
from sunset.models import image

def shortcode_lookup(type, pk):
	obj = None
	error = 'unknown'
	
	if settings.DEERFIND_SHORTCODE_TYPES.get(type, False):
		label, model = settings.DEERFIND_SHORTCODE_TYPES[type].split('.')
		try:
			model_obj = apps.get_model(app_label=label, model_name=model)
			pk = int(pk)
		except ValueError:
			error = 'invalid_pk'
		except:
			error - 'invalid_model'
		else:
			obj = model_obj.objects.filter(pk=pk).first()
	
	else:
		error = 'invalid_type'
	
	return (obj, error)

def g2_lookup(g2id=0, request=None):
	obj = None
	url = ''
	error = 'unknown'
	
	if g2id:
		try:
			g2id = int(g2id)
		except ValueError:
			error = 'invalid'
		else:
			mapcheck = g2map.objects.filter(g2id=g2id).select_related('image', 'image__cat', 'category')
			if mapcheck.exists():
				mapobj = mapcheck.first()
				if mapobj.retracted:
					error = 'retracted'
				elif mapobj.image:
					obj = mapobj.image
					error = 'found_image'
				elif mapobj.category:
					obj = mapobj.category
					error = 'found_cat'
				
				if obj:
					access_check, access_status = obj.can_view(request)
					if access_check:
						url = obj.get_absolute_url()
					else:
						error = access_status
			else:
				error = 'no_g2map'
	else:
		error = 'invalid'
	
	return (url, error)


class urlpath(object):
	raw_path = None
	path_parts = []
	dir_separator = '/'
	to_lower = False
	
	basename = ''		# Last portion of the path, whatever it is
	filename = ''		# Basename without file extension, if it has one
	filetype = ''		# File extension, if it has one
	cwd = ''			# Working dir; immediate parent if basename is a filename
	root_dir = ''		# Highest-level directory other than root
	is_file = False		# Indicates whether this is a file or directory
	
	def __init__(self, url, *args, **kwargs):
		self.dir_separator = kwargs.pop('separator', self.dir_separator)
		self.to_lower = kwargs.pop('force_lower', self.to_lower)
		self.raw_path = self.set_case(url)
		self.split_path()
	
	def set_case(self, input):
		if self.to_lower:
			return input.lower()
		else:
			return input
	
	def split_path(self):
		self.path_parts = self.raw_path.split(self.dir_separator)
		self.path_parts = [x for x in self.path_parts if x]	# I will never comprehend list comprehension
		
		self.basename = self.last_path_part()
		if '.' in self.last_path_part():
			# Only do this if basename is a file
			self.basename = self.path_parts.pop(-1)
			self.filename, self.filetype = self.basename.rsplit('.', 1)
			self.is_file = True
		
		self.cwd = self.last_path_part()
		self.root_dir = self.first_path_part()
	
	def last_path_part(self):
		if self.path_parts:
			return self.path_parts[-1]
		else:
			return ''
	
	def first_path_part(self):
		if self.path_parts:
			return self.path_parts[0]
		else:
			return ''
	
	@property
	def depth(self):
		return len(self.path_parts)
	
	@property
	def dir_full(self):
		if self.path_parts:
			return self.dir_separator.join(self.path_parts)
		else:
			return ''


#	Temporary tools for building the G2 object map

def map(img, g2):
	cur_img = image.objects.get(pk=img)
	return g2map.objects.create(g2id=g2, image=cur_img)

def fix(g2):
	return g2raw.objects.filter(g2id=g2).update(matched=True)

def destination_map():
	g2_cur_list = g2map.objects.all()
	dest_map = {}
	for item in g2_cur_list:
		dest_map[item.g2id] = item
	return dest_map

def match_raw():
	dest_map = destination_map()
	matched_count = 0
	raw_items = g2raw.objects.filter(matched=False)
	for item in raw_items:
		if dest_map.get(item.g2id, False):
			item.matched = True
			item.save()
			matched_count = matched_count + 1
	
	return matched_count

def unmatched():
	types = {}
	raw_items = g2raw.objects.all().exclude(matched=True)
	for item in raw_items:
		if types.get(item.type, False):
			types[item.type] = types[item.type] + 1
		else:
			types[item.type] = 1
	
	return types

def map_children():
	dest_map = destination_map()
	raw_items = g2raw.objects.filter(matched=True, type="GalleryPhotoItem")
	new_g2maps = []
	for item in raw_items:
		if dest_map.get(item.g2id, False):
			dest_obj = False
			if dest_map[item.g2id].image:
				dest_obj = dest_map[item.g2id].image
				if item.creation_timestamp:
					image.objects.filter(pk=dest_obj.pk).update(timestamp_upload=item.creation_timestamp)
				children = item.get_descendants()
				if children.exists():
					for child in children:
						if not dest_map.get(child.g2id, False):
							new_g2maps.append(g2map(image=dest_obj, g2id=child.g2id))
							child.matched=True
							child.save()
			elif dest_map[item.g2id].category:
				dest_obj = dest_map[item.g2id].category
				children = item.get_descendants()
				if children.exists():
					for child in children:
						if not dest_map.get(child.g2id, False):
							new_g2maps.append(g2map(category=dest_obj, g2id=child.g2id))
							child.matched=True
							child.save()
			else:
				children = item.get_descendants()
				if children.exists():
					for child in children:
						if not dest_map.get(child.g2id, False):
							new_g2maps.append(g2map(g2id=child.g2id))
							child.matched=True
							child.save()
	return g2map.objects.bulk_create(new_g2maps)
