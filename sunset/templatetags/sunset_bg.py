#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Template Tags
#	bg_filename:	Returns a url to a background image fitting the given tags
#	bg_info:		Returns text giving a title and info link for the current background
#	=================

import random

from django import template
from django.conf import settings
from django.db.models import Q
from django.utils.safestring import mark_safe

from awi_utils.utils import notify
from sunset.models import image, background_tag

register = template.Library()
cur_background = False
display_footer_info = True

@register.simple_tag(takes_context=True)
def bg_filename(context, input_string=''):
	global cur_background
	global display_footer_info
	bg_selected = False
	bg_array = False
	
	if context.get('image', False):
		# First check:  If bg_type is current_image, just set the current image as the background.
		bg_selected = context.get('image', False)
		bg_array = []
		display_footer_info = False
	elif context.get('category', False):
		# Second check:  Try to pick something from the current category, or a specified one.
		display_footer_info = True
		cur_cat_id = context['category'].pk
		
		bg_array = image.objects.filter(cat_id=cur_cat_id).filter(featured=True, assets__type='bg').select_related('cat')
		if not bg_array.exists():
			bg_array = image.objects.filter(bg_tags__category__id=cur_cat_id).filter(assets__type='bg').select_related('cat')
	elif context.get('tag', False):
		# Third check:  If bg_type is current_tag, try to pick something from the current tag.
		display_footer_info = True
		bg_array = image.objects.filter(tags=context.get('tag', False), featured=True, assets__type='bg').select_related('cat')
	elif input_string:
		# Last check:  If we have a background_tag, use it.
		display_footer_info = True
		bg_array = image.objects.filter(bg_tags__tag=input_string, assets__type='bg').select_related('cat')
	
	if not bg_array and not bg_selected:
		# If nothing is set yet, use a default image.
		display_footer_info = True
		bg_array = image.objects.filter(bg_tags__default=True).filter(assets__type='bg').select_related('cat')
		if not bg_array.exists():
			# Despite our best efforts, there is no suitable background image.  So we'll use a static default.
			display_footer_info = False
			cur_background = False
			if settings.SUNSET_BG_NOTIFY_FAIL:
				notify(subject='Sunset Background Failure', msg="A background image object could not be found.")
			return '%ssunset/blank.png' % settings.STATIC_URL
	
	if not bg_selected:
		bg_selected = random.choice(bg_array)
	
	cur_background = bg_selected
	cur_bg_asset = bg_selected.assets.get(type='bg')
	
	if cur_bg_asset:
		return cur_bg_asset.get_url()
	else:
		return ''

@register.simple_tag
def bg_info(input_string=''):
	global cur_background
	global display_footer_info
	
	if display_footer_info:
		bg_selected = cur_background
		return mark_safe('Background Photo:  <a href="%s">%s</a>' % (bg_selected.get_absolute_url(), str(bg_selected)))
	else:
		return ' ';
