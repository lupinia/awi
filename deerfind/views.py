#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	not_found:	Tries to find a redirect before giving up and showing a 404 error.  Uses a list of standard finder functions (settings.DEERFIND_FINDERS), one per content type.
#	g2_finder:	Finder for Gallery2 legacy support.  It's in this file because that's handled by this app.
#	=================

from django.http import HttpResponsePermanentRedirect, HttpResponseNotFound

from deerfind.models import pointer,hitlog

def g2_finder(request):
	import os
	from deerfind.models import g2map
	from django.core.urlresolvers import reverse
	return_data = (False,'')
	
	basename=os.path.basename(request.path)
	if '.' in basename:
		search_slug_list = basename.split('.')
		search_slug = search_slug_list[0]
	else:
		search_slug = basename
	
	if '.g2' in basename or request.GET.get('g2_itemId',''):
		if '.g2' in basename:
			gallery_id = search_slug
		else:
			gallery_id = request.GET.get('g2_itemId','')
		
		if gallery_id and isinstance(gallery_id, (int,long)):
			gallery_check=g2map.objects.select_related('category', 'image').filter(g2id=gallery_id)
			if gallery_check.exists():
				if gallery_check[0].category:
					access_check = gallery_check[0].category.can_view(request)
					if access_check[0]:
						return_data = (True,reverse('category',kwargs={'cached_url':gallery_check[0].category.cached_url,}))
				elif gallery_check[0].image:
					access_check = gallery_check[0].image.can_view(request)
					if access_check[0]:
						return_data = (True,reverse('image_single',kwargs={'cached_url':gallery_check[0].image.cat.cached_url,'slug':gallery_check[0].image.slug}))
	
	return return_data

def not_found(request):
	return_url = False
	
	#	First, make sure we're here for an actual 404, instead of "found, but not part of this site", to prevent a redirect loop
	if request.session.get('deerfind_norecover',False):
		return_url=False
		request.session['deerfind_norecover'] = False
	else:
		request.session['deerfind_norecover'] = False		# Always reset, just in case.
		
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
			#	Time to go digging.  The plan here is to check each known finder function.
			#	Finder functions should receive request as a parameter, and return a tuple;
			#		first value boolean (match found)
			#		second value a string (empty if no match, root-relative URL if match)
			from django.conf import settings
			from django.utils.module_loading import import_string
			
			finder_list = settings.DEERFIND_FINDERS
			
			for finder in finder_list:
				finder_function = import_string(finder)
				url_check = finder_function(request)
				if url_check[0]:
					return_url = url_check[1]
					break
		
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
