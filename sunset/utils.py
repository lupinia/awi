#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions/Objects
#	watermark(original):		When passed a Pillow image object, returns a watermarked version of it, if a source image for the watermark is defined in settings.SUNSET_WATERMARK_IMAGE.
#	hash_file(f):				When passed a file object, returns an SHA-256 hash of it.
#	sunset_embed(body,request):	When passed a string, returns a version of that string with <sunset /> image tags replaced with proper <a><img /></a> tags.  Request is an optional parameter for the security check.
#	=================

import hashlib

from django.conf import settings

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, Tag, Comment
from PIL import Image

from awi_access.models import access_query

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

def sunset_embed(body, request=False):
	# Moved the input down here to avoid a circular import
	from sunset.models import image
	self_closing = ['sunset',]
	
	if body and "<sunset" in body:
		body_raw = BeautifulSoup(body, selfClosingTags=self_closing)
		imglist = body_raw.findAll('sunset')
		
		for imgtag in imglist:
			err = 'Unknown error parsing Sunset embed tag'
			new_tag = ''
			img_pk = imgtag.get('id',False)
			cur_type = imgtag.get('type','icon')
			if img_pk:
				img_check = image.objects.filter(pk=int(img_pk)).filter(access_query(request)).select_related('cat')
				
				if img_check:
					cur_img = img_check.first()
					asset_check = cur_img.assets.filter(type=cur_type)
					
					if asset_check:
						cur_asset = asset_check.first()
						new_tag = BeautifulSoup(selfClosingTags=self_closing)
						new_a = Tag(new_tag, 'a')
						new_img = Tag(new_tag, 'img')
						
						new_a['class'] = 'sunset_embed sunset_%s' % cur_type
						new_a['href'] = cur_img.get_absolute_url()
						new_a['title'] = cur_img
						
						new_img['alt'] = cur_img
						new_img['title'] = cur_img
						
						new_img['src'] = cur_asset.get_url()
						
						new_tag.insert(0, new_a)
						new_a.insert(0, new_img)
						err = False
					
					else:
						err = 'Sunset image asset type specified in embed tag was not found'
				
				else:
					err = 'Sunset image specified in embed tag was not found'
			
			else:
				err = 'Invalid or missing image ID in Sunset embed tag'
			
			if err:
				imgtag.replaceWith(Comment('%s.  Original was:  %s' % (err, imgtag)))
			else:
				imgtag.replaceWith(new_tag)
		
		return unicode(body_raw)
	
	else:
		# Nothing to do.
		return body
