#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions/Objects
#	=================

import hashlib

from django.conf import settings

from PIL import Image

def watermark(original):
	if settings.SUNSET_WATERMARK_IMAGE:
		watermark = Image.open(settings.SUNSET_WATERMARK_IMAGE)
		img_marked = original.copy()
		if img_marked.mode != watermark.mode:
			img_marked = img_marked.convert(mode=watermark.mode)
		
		if img_marked.width < watermark.width+40 or img_marked.height < watermark.height+40:
			watermark.thumbnail((img_marked.width-40, img_marked.height-40), Image.LANCZOS)
		
		img_marked.paste(watermark, (img_marked.width-watermark.width-20,img_marked.height-watermark.height-20), watermark)
		
		if img_marked.mode != original.mode:
			img_marked = img_marked.convert(mode=original.mode)
		
		return img_marked
	else:
		return original

def hash_file(f):
	if f:
		hash = hashlib.sha256()
		for chunk in f.chunks():
			hash.update(chunk)
		hash_result = hash.hexdigest()
		return hash_result
	else:
		return False