#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Template Tags
#	=================

from django import template
from django.conf import settings

register = template.Library()

def get_cur_type(value):
	return settings.SEARCH_RESULT_DATA.get(value, {})

def result_template(value):
	return get_cur_type(value).get('template', settings.SEARCH_RESULT_TEMPLATE_DEFAULT)

def result_icon(value):
	return get_cur_type(value).get('default_icon', 'content')

def result_type(value):
	return get_cur_type(value).get('display_name', '')

def text_item_width(value, min=135):
	calculated = len(unicode(value)) * 7 # type: ignore
	min_default = 135
	try:
		min_width = int(min)
	except:
		min_width = min_default
	
	if calculated > min_width:
		return calculated
	else:
		return min_width

register.filter(result_template)
register.filter(result_icon)
register.filter(result_type)
register.filter(text_item_width)
