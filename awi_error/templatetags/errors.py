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
from awi_error.models import error
register = template.Library()

def error_display(input_string):
	error_data = error.objects.get(error_key=input_string)
	if error_data:
		error_output = '<div class="error error_'+error_data.severity+'">'+error_data.message+'</div>'
	else:
		error_output = '<div class="error error_critical">An unspecified/undefined error has occurred.  Error code was "'+input_string+'".</div>'
	return error_output

register.simple_tag(error_display)
