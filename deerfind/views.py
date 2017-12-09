#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	not_found:  Tries to find a redirect before giving up and showing a 404 error.  Uses a list of standard finder functions (settings.DEERFIND_FINDERS), usually one per app or content type (but not necessarily).
#	search_view:  Primary search results/search form view.
#	
#	Helper Functions  
#	g2_finder:  Finder for Gallery2 legacy support.  It's in this file because that's handled by this app.
#	=================

import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.template import Context, loader
from django.utils.module_loading import import_string

from haystack.generic_views import FacetedSearchView
from haystack.query import SearchQuerySet, SQ
from haystack.inputs import AutoQuery

from awi_access.models import check_mature, access_search
from deerfind.forms import simple_search_form
from deerfind.models import pointer, hitlog

#	404 Handler
def not_found(request):
	return_url = False
	
	#	First, make sure we're here for an actual 404, instead of "found, but not part of this site", to prevent a redirect loop
	if request.session.get('deerfind_norecover',False):
		return_url=False
		request.session['deerfind_norecover'] = False
	else:
		request.session['deerfind_norecover'] = False		# Always reset, just in case.
		
		#	Simple at first, check a list of known-bad URLs for redirects.
		pointer_obj = pointer.objects.filter(old_url=request.path).first()
		
		if pointer_obj:
			return_url = pointer_obj.new_url
			
			#	Log hits to known-bad URLs, to gauge whether the redirect is still necessary.
			if pointer_obj.log_hits:
				hitlog_fields = {
					'pointer': pointer_obj, 
					'user_agent': unicode(request.META.get('HTTP_USER_AGENT','')), 
					'accept': unicode(request.META.get('HTTP_ACCEPT','')), 
					'accept_encoding': unicode(request.META.get('HTTP_ACCEPT_ENCODING','')), 
					'accept_language': unicode(request.META.get('HTTP_ACCEPT_LANGUAGE','')), 
					'host': unicode(request.META.get('HTTP_HOST','')), 
					'query_string': unicode(request.META.get('QUERY_STRING','')), 
					'remote_addr': unicode(request.META.get('REMOTE_ADDR','')), 
				}
				
				if request.META.get('HTTP_REFERER','').startswith('http'):
					hitlog_fields['referer'] = unicode(request.META.get('HTTP_REFERER',''))
				elif request.META.get('HTTP_REFERER',''):
					hitlog_fields['referer'] = '(Redacted - Possibly Malicious)'
				else:
					hitlog_fields['referer'] = ''
				
				hitlog_obj = hitlog.objects.create(**hitlog_fields)
		
		else:
			#	Time to go digging.  The plan here is to check each known finder function.
			#	Finder functions should receive request as a parameter, and return a tuple;
			#		first value boolean (match found)
			#		second value a string (empty if no match, root-relative URL if match)
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
		template = loader.get_template('deerfind/404.html')
		
		#	Get the attempted URL to display to the user
		if request.META.get('QUERY_STRING',False):
			context_path=request.path+'?'+request.META.get('QUERY_STRING','')
		else:
			context_path=request.path
		context=Context({'old_url':context_path})
		
		#	Run a search query, in case what they're looking for can be found with search.
		#	First, let's clean up the URL and turn it into something we can search.
		basename = os.path.basename(request.path)
		if '.' in basename:
			search_path = basename.split('.')[0]
		else:
			search_path = basename
		
		sqs = access_search(SearchQuerySet(), request).filter(SQ(url=AutoQuery(search_path)) | SQ(title=AutoQuery(search_path)))
		if sqs.count():
			result = sqs.best_match()
			context['search_result'] = True
			
			if settings.SEARCH_RESULT_DATA.get(result.content_type(), {}).get('display_name', False):
				context['search_result_title'] = '%s (%s)' % (result.title, settings.SEARCH_RESULT_DATA[result.content_type()]['display_name'])
			else:
				context['search_result_title'] = result.title
			
			context['search_result_url'] = result.url
		
		else:
			context['search_result'] = False
		
		context['search_query'] = search_path.replace(' ', '+')
		
		#	Here's the 404 template.  Sorry we couldn't find what you were looking for!
		return HttpResponseNotFound(content=template.render(context), content_type='text/html; charset=utf-8')


#	Finder:  Gallery2 Legacy Compatibility
def g2_finder(request):
	from deerfind.models import g2map
	return_data = (False,'')
	
	basename = os.path.basename(request.path)
	if '.g2' in basename:
		search_slug_list = basename.split('.')
		search_slug = search_slug_list[0]
	else:
		search_slug = basename
	
	if '.g2' in basename or request.GET.get('g2_itemId',''):
		if '.g2' in basename:
			gallery_id = search_slug
		else:
			gallery_id = request.GET.get('g2_itemId','')
		
		if gallery_id and gallery_id.isdigit():
			gallery_check=g2map.objects.select_related('category', 'image').filter(g2id=gallery_id)
			if gallery_check.exists():
				if gallery_check[0].category:
					access_check = gallery_check[0].category.can_view(request)
					if access_check[0]:
						return_data = (True,gallery_check[0].category.get_absolute_url())
				elif gallery_check[0].image:
					access_check = gallery_check[0].image.can_view(request)
					if access_check[0]:
						return_data = (True,gallery_check[0].image.get_absolute_url())
	
	return return_data


#	Primary Search View
class search_view(FacetedSearchView):
	form_class = simple_search_form
	facet_fields = ['pub_date', 'category', 'tags']
	
	def get_queryset(self):
		queryset = access_search(super(search_view, self).get_queryset(), self.request)
		return queryset.load_all()
	
	def get_context_data(self, *args, **kwargs):
		context = super(search_view, self).get_context_data(*args, **kwargs)
		context['highlight_featured'] = True
		
		if context.get('query',False):
			context['paginator_vars'] = [('q', context.get('query',False)), ]
		
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		context['breadcrumbs'].append({'url':reverse('haystack_search'), 'title':'Search'})
		
		return context
	
	def form_valid(self, form):
		# Dear Haystack:
		# Why do I have to override and re-write this to make suggestions work correctly?
		# You're starting to get on my nerves.
		
		# Copied from Haystack source
		self.queryset = form.search()
		context = self.get_context_data(**{
			self.form_name: form,
			'query': form.cleaned_data.get(self.search_field),
			'object_list': self.queryset,
			
			# Adding this here, since it didn't work from within get_context_data
			'spelling_suggestion':self.queryset.spelling_suggestion(form.cleaned_data.get(self.search_field)),
		})
		return self.render_to_response(context)
