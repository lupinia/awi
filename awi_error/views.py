#	Awi Error (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	system_error:	500 error handler.  Just displays a template, further information is emailed.
#	denied_error:	403 error handler.  Just displays a template.
#	=================

import sys

from django.http import HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render
from django.template import Context, loader

def system_error(request):
	template=loader.get_template('awi_error/500.html')
	type, value, tb = sys.exc_info()
	if value is None:
		value = 'No exception info found'
	context=Context({'error_value':value,})
	
	return HttpResponseServerError(content=template.render(context), content_type='text/html; charset=utf-8')

def denied_error(request):
	template=loader.get_template('awi_error/403.html')
	if request.META.get('QUERY_STRING',False):
		context_path=request.path+'?'+request.META.get('QUERY_STRING','')
	else:
		context_path=request.path
	context=Context({'bad_url':context_path})
	
	return HttpResponseForbidden(content=template.render(context), content_type='text/html; charset=utf-8')