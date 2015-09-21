#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	not_found:	Tries to find a redirect before giving up and showing a 404 error.
#	=================

from django.http import HttpResponsePermanentRedirect, HttpResponseNotFound

from deerfind.models import pointer,hitlog

def not_found(request):
	return_url = False
	
	#	Simple at first, check a list of known-bad URLs for redirects.
	url_check=pointer.objects.filter(old_url=request.path)
	
	if url_check.exists():
		return_url=url_check[0].new_url
		
		#	Log hits to known-bad URLs, to gauge whether the redirect is still necessary.
		hitcount=hitlog.objects.create(
			pointer=url_check[0],
			user_agent = request.META.get('HTTP_USER_AGENT',''),
			accept = request.META.get('HTTP_ACCEPT',''),
			accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING',''),
			accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE',''),
			host = request.META.get('HTTP_HOST',''),
			referer = request.META.get('HTTP_REFERER',''),
			query_string = request.META.get('QUERY_STRING',''),
			remote_addr = request.META.get('REMOTE_ADDR',''),
		)
	else:
		#	Once the content apps are finished, this will search them for possible matches before returing a 404.
		#	This is the main purpose of this app, and this feature exists in v4.1, it just needs a little re-engineering.
		pass

	if return_url:
		#	Yay!  We found a match!  No 404 for you!  :D
		return HttpResponsePermanentRedirect(return_url)
	else:
		#	If all else fails, display the 404 page
		from django.shortcuts import render
		from django.template import Context, loader
		template=loader.get_template('deerfind/404.html')
		
		#	Get the attempted URL to display to the user
		if request.META.get('QUERY_STRING',False):
			context_path=request.path+'?'+request.META.get('QUERY_STRING','')
		else:
			context_path=request.path
		context=Context({'old_url':context_path})
		
		#	Here's the 404 template.  Sorry we couldn't find what you were looking for!
		return HttpResponseNotFound(content=template.render(context), content_type='text/html; charset=utf-8')
