#	500 Error Handler

def system_error(request):
	from django.http import HttpResponseServerError
	from django.shortcuts import render
	from django.template import Context, loader
	template=loader.get_template('awi_error/500.html')
	context=Context({'none':True})
	return HttpResponseServerError(content=template.render(context), content_type='text/html; charset=utf-8')
