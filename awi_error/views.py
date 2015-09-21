#	Awi Error (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	system_error:	500 error handler.  Just displays a template, further information is emailed.
#	=================

def system_error(request):
	from django.http import HttpResponseServerError
	from django.shortcuts import render
	from django.template import Context, loader
	template=loader.get_template('awi_error/500.html')
	context=Context({'none':True})
	return HttpResponseServerError(content=template.render(context), content_type='text/html; charset=utf-8')
