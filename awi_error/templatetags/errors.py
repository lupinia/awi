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

from django import template
from django.utils.safestring import mark_safe

from awi_error.models import error

register = template.Library()

def error_display(input_string):
	error_data = error.objects.filter(error_key=input_string).first()
	if error_data:
		error_output = '<%s class="error error_%s" id="%s">%s</%s>' % (error_data.element, error_data.severity, input_string, error_data.message, error_data.element)
	else:
		error_output = '<div class="error error_critical" id="%s">An unspecified/undefined error has occurred.  Error code was "%s".</div>' % (input_string, input_string)
	return mark_safe(error_output)

register.simple_tag(error_display)
