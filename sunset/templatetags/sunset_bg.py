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
from django.core.cache import cache
from django.db.models import Q
from django.utils.safestring import mark_safe

from awi_utils.utils import notify
from sunset.models import image, background_tag

register = template.Library()
display_footer_info = True
cur_background_title = ""
cur_background_info_url = ""

def check_cache(prefix):
	check = cache.get('sunsetbg_%s' % prefix)
	if check is None:
		return (False, {})
	else:
		values = {}
		values['url'], values['title'], values['info_url'] = check.split('|!|')
		return (True, values)

def store_cache(prefix, url, info_title="", info_url="", timeout=300):
	value = '%s|!|%s|!|%s' % (url, info_title, info_url)
	cache.set('sunsetbg_%s' % prefix, value, 300)

def set_bg(image_obj, cache_key="", cache_timeout=0):
	global cur_background_title
	global cur_background_info_url
	global display_footer_info
	
	cur_bg_asset = image_obj.assets.get(type='bg')
	if cur_bg_asset:
		bg_url = cur_bg_asset.get_url()
		if display_footer_info:
			cur_background_title = str(image_obj)
			cur_background_info_url = image_obj.get_absolute_url()
		
		if cache_key and cache_timeout:
			store_cache(cache_key, bg_url, cur_background_title, cur_background_info_url, cache_timeout)
		
		return bg_url
	else:
		return ''

def set_bg_from_cache(cache_data):
	global cur_background_title
	global cur_background_info_url
	global display_footer_info
	
	if display_footer_info:
		cur_background_title = cache_data.get('title', '')
		cur_background_info_url = cache_data.get('info_url', '')
	
	return cache_data.get('url', '')


@register.simple_tag(takes_context=True)
def bg_filename(context, input_string=''):
	global display_footer_info
	cache_key = ""
	cache_timeout = 300
	
	if context.get('image', False):
		# First check:  If bg_type is current_image, just set the current image as the background.
		bg_selected = context.get('image', False)
		display_footer_info = False
		return set_bg(bg_selected)
	else:
		display_footer_info = True
		bg_query = image.objects.filter(assets__type='bg').select_related('cat')
		has_cat = False
		
		# Step 1:  Define query parameters, as narrowly as possible
		if context.get('category', False):
			# Second check:  Try to pick something from the current category, or a specified one.
			cur_cat_id = context['category'].pk
			cache_key = 'cat_%d' % cur_cat_id
			cache_timeout = 900
			has_cat = cur_cat_id
			
			bg_query_cat = bg_query.filter(cat_id=cur_cat_id).filter(featured=True)
			# Special case:  If there's nothing directly in this category, use the category's background tag
			if bg_query_cat:
				bg_query = bg_query_cat
			else:
				bg_query = bg_query.filter(bg_tags__category__id=has_cat)
		
		elif context.get('tag', False):
			# Third check:  If bg_type is current_tag, try to pick something from the current tag.
			cur_tag = context.get('tag', False)
			cache_key = 'tag_%d' % cur_tag.pk
			cache_timeout = 900
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
			return set_bg_from_cache(cached_data)
		
		else:
			if not bg_query:
				# If nothing is set yet, use a default image
				bg_query = image.objects.filter(bg_tags__default=True, assets__type='bg').select_related('cat')
			
			# Ok, time to check for results and actually render something!
			if bg_query:
				return set_bg(random.choice(bg_query), cache_key, cache_timeout)
			
			else:
				# Despite our best efforts, there is no suitable background image.  So we'll use a static default.
				display_footer_info = False
				if settings.SUNSET_BG_NOTIFY_FAIL:
					notify(subject='Sunset Background Failure', msg="A background image object could not be found.")
				return '%ssunset/blank.png' % settings.STATIC_URL

@register.simple_tag
def bg_info(input_string=''):
	global cur_background_title
	global cur_background_info_url
	global display_footer_info
	
	if display_footer_info:
		return mark_safe('Background Photo:  <a href="%s">%s</a>' % (cur_background_info_url, cur_background_title))
	else:
		return ' ';
