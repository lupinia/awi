#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Forms
#	=================

from django.conf import settings

from haystack.forms import FacetedSearchForm
from haystack.inputs import AutoQuery
from haystack.query import SQ

class simple_search_form(FacetedSearchForm):
	def __init__(self, *args, **kwargs):
		# I shouldn't have to override this to set a placeholder for the search form's main field.
		super(simple_search_form, self).__init__(*args, **kwargs)
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
