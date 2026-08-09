#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for error handling
#	=================

import sys

from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseServerError, HttpResponseBadRequest
from django.template import loader

class BadRequest(SuspiciousOperation):
	"""The request is malformed and cannot be processed."""
	pass

def system_error(request):
	"""Custom error page for 500 errors"""
	template=loader.get_template('500.html')
	type, value, tb = sys.exc_info()
	if value is None:
		value = 'No exception info found'
	
	context = {
		'error_value':value,
		'title_page':"System Error (HTTP 500)",
		'response_code':'500',
		'response_code_name':'Internal Server Error',
	}
	
	return HttpResponseServerError(content=template.render(context, request), content_type='text/html; charset=utf-8')

def request_error(request, exception=None):
	"""Custom error page for 400 errors"""
	template=loader.get_template('400.html')
	
	if exception:
		value = exception
	else:
		value = 'bad request (unknown)'
	
	context = {
		'error_value':value,
		'title_page':"Bad Request (HTTP 400)",
		'response_code':'400',
		'response_code_name':'Bad Request',
	}
	
	return HttpResponseBadRequest(content=template.render(context, request), content_type='text/html; charset=utf-8')
