#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for Django admin views
#	=================

from django.utils.safestring import mark_safe

from awi.utils.types import is_int, is_string

def imgfield_as_html(obj, imgfield, urlfield=None, width=None, height=None, alt='', default=None, darkbg=False):
	"""
	imgfield_as_html(obj, imgfield (str), **options) -> unicode or None
	
	Basic HTML tag output for rendering image fields as images in model admin views.
	Only returns an <img /> tag, or None.
	Parameters:
		obj:  The object to pull an image field from
		imgfield:  String, specifies the name of an ImageField on obj
		urlfield:
			String, specifies the name of the property or field containing a full URL to the image
			Defaults to {imgfield}_url
		width:
			Set to a string to specify the name of the property or field containing the image width
			Set to an integer to specify the value manually
			Defaults to {imgfield}.width
		height:
			Set to a string to specify the name of the property or field containing the image height
			Set to an integer to specify the value manually
			Defaults to {imgfield}.height
		alt:
			String, specifies the name of the property or field containing the alt text
			If value doesn't exist as a property or field on the model, this will be interpreted as a manual override
			Defaults to str(obj)
		default:
			Controls the return behavior when the selected image field is empty
			If set to a string formatted as a URL, this will be used as a fallback/placeholder image
			If set to a string that exists as an attribute of obj, this will use the value of that attribute
			Defaults to None, which will force this function to return None instead of an img tag
		darkbg (bool):
			Set to True to apply a dark background color to the image
			Defaults to False
	"""
	img_url = None
	img_width = 0
	img_height = 0
	img_alt = None
	img_attrs = []
	img_classes = []
	
	# Set up defaults
	if not urlfield:
		urlfield = '%s_url' % imgfield
	
	if width is not None and is_int(width):
		img_width = width
	if height is not None and is_int(height):
		img_height = height
	
	if darkbg:
		img_classes.append('admin_image_field_darkbg')
	
	if obj:
		if getattr(obj, imgfield, None):
			# imgfield exists and is not empty
			img_url = getattr(obj, urlfield, None)
			if is_string(width):
				img_width = getattr(obj, width, img_width)
			else:
				img_width = getattr(obj, imgfield).width
			
			if is_string(height):
				img_height = getattr(obj, height, img_height)
			else:
				img_height = getattr(obj, imgfield).height
		
		if img_url is None:
			# Something went wrong, try the default
			if is_string(default):
				img_url = getattr(obj, default, default)
			else:
				# Default is not a string (probably None), so just jump out here
				return None
		
		if alt:
			img_alt = getattr(obj, alt, alt)
		else:
			img_alt = unicode(obj)	#type:ignore
	
	else:
		if is_string(default) and '://' in default:
			img_url = default
		else:
			# No object and no default, so don't even bother doing the rest
			return None
	
	# Let's see if we got a usable image out of that
	if img_url:
		img_attrs.append('src="%s"' % img_url)
		
		if img_width and img_height:
			img_attrs.append('width="%d"' % img_width)
			img_attrs.append('height="%d"' % img_height)
		
		if img_alt:
			img_attrs.append('alt="%s"' % img_alt)
			img_attrs.append('title="%s"' % img_alt)
		
		if img_classes:
			img_attrs.append('class="%s"' % ' '.join(img_classes))
		
		return mark_safe(u'<img %s />' % ' '.join(img_attrs))
	
	else:
		return None
