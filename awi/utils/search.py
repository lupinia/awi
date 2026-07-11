#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for Haystack search
#	=================

from django.conf import settings

from haystack.forms import FacetedSearchForm as BaseFacetedSearchForm
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from haystack.inputs import AutoQuery
from haystack.query import SQ

# Abstract base classes
class FacetedSearchForm(BaseFacetedSearchForm):
	def __init__(self, *args, **kwargs):
		# I shouldn't have to override this to set a placeholder for the search form's main field.
		super(FacetedSearchForm, self).__init__(*args, **kwargs)
		self.fields['q'].widget.attrs['placeholder'] = 'Search...'
	
	def search(self):
		# Apparently, I basically have to rewrite this entire function in order to search on more than one field.
		# That includes rewriting it for both FacetedSearchForm and SearchForm
		# Dear Haystack:  Make this easier.  PLEASE.  Allow me to specify the default fields as a list in the settings or something.
		# ...Actually, that's not a bad idea, so I'll do it for you, Haystack.
		
		# Error handling, copied from Haystack source (SearchForm)
		if not self.is_valid():
			return self.no_query_found()
		
		if not self.cleaned_data.get('q'):
			return self.no_query_found()
		
		# Ok, now the actually-interesting part
		# We need to search on more than just the document field
		# And I really don't want to rewrite this file if I change/add fields, because I shouldn't have to.
		# First, this variable needs to exist in order for the loop to work.
		filters = None
		
		# Now, we need the list of default fields.
		# I'm not currently using a 'HAYSTACK_' settings variable name, because it's not my namespace and collisions are bad.
		# So, if DEERFIND_DEFAULT_SEARCH_FIELDS exists, we want to use that.
		# If DEERFIND_DEFAULT_SEARCH_FIELDS doesn't exist, we want to fall back on a single-element list containing the default.
		# And if *that* doesn't exist for some reason, we'll just use 'content'
		# getattr is fun :)
		fieldlist = getattr(settings, 'DEERFIND_DEFAULT_SEARCH_FIELDS', [getattr(settings, 'HAYSTACK_DOCUMENT_FIELD', 'content'),])
		
		# This is my favorite part!
		# We'll loop through the fieldlist to get the names of the search fields.
		# If there's only one, then this whole endeavor was a little silly, but we'll add it anyway.
		# If there's more than one, it will chain them together with OR operators.
		# To actually inject arbitrary field names into SQ objects, I had to get a little creative and unorthodox:
		# We'll create an on-the-fly dictionary, with the field name as the key, and an AutoQuery object as the value.
		# Then we'll immediately unpack it into kwargs using the ** operator.
		# I feel like this sort of thing shouldn't actually work, but I'm glad it does!
		for field in fieldlist:
			if filters is None:
				filters = SQ(**{field:AutoQuery(self.cleaned_data['q']),})
			else:
				filters = filters | SQ(**{field:AutoQuery(self.cleaned_data['q']),})
		
		sqs = self.searchqueryset.filter(filters)
		# See, Haystack?  That wasn't so hard.
		# It's not exactly the prettiest code, admittedly, but it gets the job done nicely.
		# And I wasn't even putting that much effort into this.
		
		# Wrapping up, copied from Haystack source (FacetedSearchForm)
		for facet in self.selected_facets:
			if ":" not in facet:
				continue
			
			field, value = facet.split(":", 1)
			
			if value:
				sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))
		
		return sqs

class FacetedSearchView(BaseFacetedSearchView):
	form_class = FacetedSearchForm
	title_page = "Search"
	
	def get_context_data(self, *args, **kwargs):
		context = super(FacetedSearchView, self).get_context_data(*args, **kwargs)
		
		# Setting sensible defaults for this site
		context['highlight_featured'] = True
		context['title_page'] = self.title_page
		
		if not context.get('breadcrumbs',False):
			# Append the rest in the actual view
			context['breadcrumbs'] = []
		
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
