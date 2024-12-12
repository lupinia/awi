#	Awi Error (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	system_error:	500 error handler.  Just displays a template, further information is emailed.
#	=================

import sys

from django.http import HttpResponseServerError
from django.template import loader

def system_error(request):
	"""Custom error page for 500 errors"""
	template=loader.get_template('500.html')
	type, value, tb = sys.exc_info()
	if value is None:
		value = 'No exception info found'
	context = {'error_value':value, 'title_page':"System Error (500)",}
	
	return HttpResponseServerError(content=template.render(context, request), content_type='text/html; charset=utf-8')
