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
from django.template import loader

def system_error(request):
	template=loader.get_template('awi_error/500.html')
	type, value, tb = sys.exc_info()
	if value is None:
		value = 'No exception info found'
	context = {'error_value':value, 'title_page':"System Error (500)",}
	
	return HttpResponseServerError(content=template.render(context, request), content_type='text/html; charset=utf-8')

def denied_error(request):
	template=loader.get_template('awi_error/403.html')
	if request.META.get('QUERY_STRING',False):
		context_path=request.path+'?'+request.META.get('QUERY_STRING','')
	else:
		context_path=request.path
	context = {'bad_url':context_path, 'title_page':"Access Denied (403)",}
	
	return HttpResponseForbidden(content=template.render(context, request), content_type='text/html; charset=utf-8')