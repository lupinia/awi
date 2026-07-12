#	Dagasi - Content Security (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Search Components
#	=================

from django.conf import settings

from haystack import indexes
from haystack.query import SearchQuerySet, SQ

from awi.utils import types as typeutils
from awi.utils.search import params_to_SQ

class SecuredSearchQuerySet(SearchQuerySet):
	"""
	A version of SecuredQuerySet modified for Haystack queries
	Because SearchQuerySets work a little differently from QuerySets,
	it's more reliable to use .exclude() for most of this.
	
	Unpublished items should not be indexed at all, so this assumes they won't be
	"""
	def public(self, include_hidden=False, include_mature=False, for_site=None):
		"""
		Retrieve only content that's publicly visible
		Additional parameters for selectively overriding hidden or mature settings
		"""
		self = self._site_filter(for_site)
		exclusions = {'security__gt':0,}
		
		if not include_hidden:
			exclusions['hidden'] = True
		if not include_mature:
			exclusions['mature'] = True
		
		return self.exclude(**exclusions)
	
	def for_user(self, user=None, include_hidden=False, include_mature=False, for_site=None):
		"""
		Retrieve only content that the specified user can view
		Additional parameters for selectively overriding hidden or mature settings
		"""
		pass
	
	def for_request(self, request=None, force_hidden=None):
		"""
		Retrieve only content that the specified request can view, including user access
		Pass force_hidden parameter to override hidden content preferences from request.userprefs
		"""
		pass
	
	def created_by(self, user, include_contributors=None):
		"""
		Performs a query filtering only objects created or contributed to by the specified user.
		Returns queryset.none() if user does not exist
		"""
		pass
	
	def published(self, for_site=None, **kwargs):
		"""
		Performs a query filtering all items that are published, regardless of other factors.
		Pass for_site parameter to override site restriction
		Pass other kwargs to add to the query
		
		All indexed objects must be published, 
		so this is basically just a proxy for .filter
		Included only for API compatibility
		"""
		pass
