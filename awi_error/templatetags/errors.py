#	Awi Error (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Template Tags
#	error_display:	Formats the specified error for its severity, and returns its error message
#	
#	TODO:	Multilingual support
#	=================

import json

from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe

from awi_error.models import error

register = template.Library()

def error_display(input_string):
	cache_data = False
	check = cache.get('awi_error_%s' % input_string)
	if check is None:
		error_data = error.objects.filter(error_key=input_string).values().first()
		cache_data = True
	else:
		error_data = json.loads(check)
	
	if error_data:
		error_output = '<%s class="error error_%s" id="%s">%s</%s>' % (error_data.get('element', 'div'), error_data.get('severity', 'critical'), input_string, error_data.get('message', 'An unknown error has occurred.'), error_data.get('element', 'div'))
		if cache_data:
			cache.set('awi_error_%s' % input_string, json.dumps(error_data), 60*60*24*7) # 1 week
	else:
		error_output = '<div class="error error_critical" id="%s">An unspecified/undefined error has occurred.  Error code was "%s".</div>' % (input_string, input_string)
	return mark_safe(error_output)

register.simple_tag(error_display)
