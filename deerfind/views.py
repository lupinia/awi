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
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseNotFound
from django.template import loader
from django.utils.module_loading import import_string

from haystack.generic_views import FacetedSearchView
from haystack.query import SearchQuerySet, SQ
from haystack.inputs import AutoQuery

from awi_access.models import check_mature, access_search
from awi_access.utils import add_new_block
from awi_access.views import denied_error
from deerfind.forms import simple_search_form
from deerfind.models import pointer
from deerfind.utils import g2_lookup, shortcode_lookup

#	404 Handler
def not_found(request, exception=None):
	return_url = False
	
	#	First, make sure we're here for an actual 404, instead of "found, but not part of this site", to prevent a redirect loop
	if request.session.get('deerfind_norecover',False):
		return_url=False
		request.session['deerfind_norecover'] = False
	elif request.session.get('deerfind_path',False):
		# Looks like the work's already been done for us!  Thanks!
		return_url = request.session['deerfind_path']
		request.session['deerfind_norecover'] = False
		request.session['deerfind_path'] = None
	else:
		request.session['deerfind_norecover'] = False		# Always reset, just in case.
		intentional_404 = False
		
		#	Second, let's check for a particular type of scanner
		if 'contact/' in request.path.lower() and 'contact+form' in request.path.lower():
			add_new_block(request.META['REMOTE_ADDR'], unicode(request.META.get('HTTP_USER_AGENT', ''))) # type: ignore
			return denied_error(request)
		
		#	Gallery2 continues to make things complicated:
		#		If the URL contains a g2_itemId in the GET query, prioritize that.
		if request.GET.get('g2_itemId',False):
			return_url, g2results = g2_lookup(request.GET.get('g2_itemId', 0), request)
			if g2results == 'retracted' or g2results == 'access_404':
				return_url = False
				intentional_404 = True
		
		#	Simple at first, check a list of known-bad URLs for redirects.
		pointer_obj = None
		if not return_url and not intentional_404:
			pointer_obj = pointer.objects.filter(old_url__iexact=request.path).first()
		
		if pointer_obj:
			return_url = pointer_obj.new_url
		
		elif not return_url and not intentional_404:
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
		context_path = request.path
		if request.META.get('QUERY_STRING',False):
			context_path = '%s?%s' % (context_path, request.META.get('QUERY_STRING',''))
		
		context = {
			'old_url':context_path,
			'title_page':"File Not Found (HTTP 404)",
			'response_code':'404',
			'response_code_name':'File Not Found',
		}
		
		#	Run a search query, in case what they're looking for can be found with search.
		#	First, let's clean up the URL and turn it into something we can search.
		#	Start by fixing the trailing slash
		if request.path.endswith('/'):
			basename = os.path.basename(request.path[:-1])
		else:
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
		return HttpResponseNotFound(content=template.render(context, request), content_type='text/html; charset=utf-8')


#	Finder:  Gallery2 Legacy Compatibility
def g2_finder(request):
	from deerfind.models import g2map
	return_data = (False,'')
	gallery_id = False
	
	# Step 1:  Try to find a valid Gallery2 item ID
	# No GET parameter, so this could be a rewritten URL with a .g2 file extension
	basename = os.path.basename(request.path)
	if '.g2' in basename:
		search_slug_list = basename.split('.')
		gallery_id = search_slug_list[0]
	
	# If we're here, we have a valid Gallery2 ID
	if gallery_id:
		return_url, g2results = g2_lookup(gallery_id, request)
		if return_url:
			return_data = (True, return_url)
	
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
		context['title_page'] = "Search"
		
		if context.get('query',False):
			context['paginator_vars'] = [('q', context.get('query',False)), ]
			context['title_page'] += ": " + context.get('query','')
			
			if context.get('is_paginated',False) and context.get('object_list',False):
				try:
					page_cur = context['page_obj'].number
					page_total = context['page_obj'].paginator.num_pages
					context['title_page'] += " (Page %d of %d)" % (page_cur, page_total)
				except KeyError:
					# Something went wrong, and this isn't that important anyway, so do nothing
					pass
		
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


#	Shortcode Handler
def shortcode_redirect(request, type, pk, **kwargs):
	target, error = shortcode_lookup(type, pk)
	if target:
		try:
			target_url = target.get_absolute_url()
			return HttpResponsePermanentRedirect(target_url)
		except:
			request.session['deerfind_norecover'] = True
			raise Http404
	else:
		request.session['deerfind_norecover'] = True
		raise Http404
