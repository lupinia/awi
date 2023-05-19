#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Template Tags
#	bg_filename:	Returns a url to a background image fitting the given tags
#	bg_info:		Returns text giving a title and info link for the current background
#	=================

import json
import random

from django import template
from django.conf import settings
from django.core.cache import cache

from awi_access.models import access_query
from awi_utils.utils import notify
from sunset.models import image

register = template.Library()
blank_bg = {
	'url':'%ssunset/blank.png' % settings.STATIC_URL,
	'display_footer_info':False,
}
global bg_data

def check_cache(prefix):
	check = cache.get('sunsetbg_%s' % prefix)
	if check is None:
		return (False, {})
	else:
		values = json.loads(check)
		return (True, values)

def store_cache(prefix, data, timeout=300):
	value = json.dumps(data)
	cache.set('sunsetbg_%s' % prefix, value, timeout)

def set_bg(image_obj, display_footer_info, cache_key="", cache_timeout=0):
	bg_data = {}
	cur_bg_asset = image_obj.assets.get(type='bg')
	if cur_bg_asset:
		bg_data['url'] = cur_bg_asset.get_url()
		bg_data['display_footer_info'] = display_footer_info
		if display_footer_info:
			bg_data['title'] = str(image_obj)
			bg_data['info_url'] = image_obj.get_absolute_url()
		
		if cache_key and cache_timeout:
			store_cache(cache_key, bg_data, cache_timeout)
	
	return bg_data


@register.simple_tag(takes_context=True)
def bg_select(context, input_string=''):
	global bg_data
	display_footer_info = False
	cache_key = ""
	cache_timeout = 900
	
	if context.get('image', False) and context.get('image', False).can_view(context.get('request', False))[0]:
		# First check:  If bg_type is current_image, just set the current image as the background.
		bg_selected = context.get('image', False)
		display_footer_info = False
		bg_data = set_bg(bg_selected, display_footer_info)
		return ''
	else:
		display_footer_info = True
		bg_query = image.objects.filter(assets__type='bg').filter(access_query(context.get('request', False))).select_related('cat')
		
		# Step 1:  Define query parameters, as narrowly as possible
		if context.get('category', False):
			# Second check:  Try to pick something from the current category, or a specified one.
			cur_cat_id = context['category'].pk
			cache_key = 'cat_%d' % cur_cat_id
			cache_timeout = 1800
			
			bg_query_cat = bg_query.filter(cat_id=cur_cat_id).filter(featured=True)
			# Special case:  If there's nothing directly in this category, use the category's background tag
			if bg_query_cat:
				bg_query = bg_query_cat
			else:
				bg_query = bg_query.filter(bg_tags__category__id=cur_cat_id)
		
		elif context.get('tag', False):
			# Third check:  If bg_type is current_tag, try to pick something from the current tag.
			cur_tag = context.get('tag', False)
			cache_key = 'tag_%d' % cur_tag.pk
			cache_timeout = 600
			bg_query = bg_query.filter(tags=cur_tag).filter(featured=True)
		
		elif input_string:
			# Fourth check:  If we have a background_tag, use it.
			cache_key = 'keyword_%s' % input_string
			bg_query = bg_query.filter(bg_tags__tag=input_string)
		
		else:
			# Special case:  If this function was invoked without parameters, use the default
			# This mostly only happens on the home page
			cache_key = 'default_bg'
			bg_query = bg_query.filter(bg_tags__default=True)
		
		# Step 2:  Check whether we've already cached a result for this query
		cache_status, cached_data = check_cache(cache_key)
		if cache_status:
			# Yay!  This was easy
			bg_data = cached_data
			return ''
		
		else:
			if not bg_query:
				# If nothing is set yet, use a default image
				bg_query = image.objects.filter(bg_tags__default=True, assets__type='bg').filter(access_query(context.get('request', False))).select_related('cat')
			
			# Ok, time to check for results and actually render something!
			if bg_query:
				bg_data = set_bg(random.choice(bg_query), display_footer_info, cache_key, cache_timeout)
				return ''
			
			else:
				# Despite our best efforts, there is no suitable background image.  So we'll use a static default.
				display_footer_info = False
				if settings.SUNSET_BG_NOTIFY_FAIL:
					notify(subject='Sunset Background Failure', msg="A background image object could not be found.")
				bg_data = blank_bg
				return ''

@register.simple_tag()
def get_bg_data():
	global bg_data
	return bg_data