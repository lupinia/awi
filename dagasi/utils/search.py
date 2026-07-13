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
		If user does not exist or is not active, return the public queryset
		If user is superuser, unfiltered queryset (no restrictions)
		Else, return the following query restrictions:
			(user is owner OR user is in contributors)
			OR (security <= 2 AND groups in user groups AND is published)
			OR (security <= 1 AND is published)
		"""
		if user and user.is_active:
			if user.is_superuser:
				# No restrictions on superusers
				return self
			else:
				params_extra = {}
				
				if for_site is None:
					# This permission check is unnecessary if it's pre-cached
					if user.has_perm('dagasi.view_cross_site'):
						for_site = 0
				
				if not include_hidden:
					params_extra['hidden'] = False
				
				if not include_mature:
					params_extra['mature'] = False
				
				# Start building a query chain
				q_objs = SQ(contributors=user.pk)
				
				# TODO: Cache group pks for user
				if user.groups.exists():
					q_objs_grp = SQ(security__lte=2) & SQ(groups__in=user.groups.all().values_list('pk', flat=True))
					if params_extra:
						q_objs_grp = q_objs_grp & params_to_SQ(params_extra)
					
					q_objs = q_objs | (q_objs_grp)
				
				# Add in the site filter only for public or all-users content
				params_extra.update(self._params_sites(for_site))
				q_objs = q_objs | (SQ(security__lte=1) & params_to_SQ(params_extra))
				
				return self.filter(q_objs)
		
		else:
			return self.public(include_hidden, include_mature, for_site)
	
	def for_request(self, request=None, force_hidden=None):
		"""
		Retrieve only content that the specified request can view, including user access
		Pass force_hidden parameter to override hidden content preferences from request.userprefs
		"""
		if request:
			include_mature = request.userprefs.get('show_mature', False)
			include_hidden = request.userprefs.get('show_hidden', False)
			if force_hidden is not None:
				include_hidden = force_hidden
			
			# Site restriction is pre-cached when we have a request
			for_site = settings.SITE_ID
			if request.userprefs.get('view_cross_site', False):
				for_site = 0
			
			# Not messing with access codes in search views, so this is simpler
			if request.user.is_authenticated():
				return self.for_user(request.user, include_hidden=include_hidden, include_mature=include_mature, for_site=for_site)
			else:
				return self.public(include_hidden=include_hidden, include_mature=include_mature, for_site=for_site)
		
		else:
			return self.public()
	
	def created_by(self, user, include_contributors=None):
		"""
		Performs a query filtering only objects created or contributed to by the specified user.
		Returns queryset.none() if user does not exist
		"""
		if include_contributors is not None:
			return NotImplemented
		
		if user:
			if hasattr(user, 'pk'):
				return self.filter(contributors=user.pk)
			elif typeutils.is_int(user):
				return self.filter(contributors=user)
			else:
				raise TypeError('user must be integer or User instance')
		
		else:
			return self.none()
	
	def published(self, for_site=None, **kwargs):
		"""
		Performs a query filtering all items that are published, regardless of other factors.
		Pass for_site parameter to override site restriction
		Pass other kwargs to add to the query
		
		All indexed objects must be published, 
		so this is basically just a proxy for .filter
		Included only for API compatibility
		"""
		self = self._site_filter(for_site)
		if kwargs:
			self = self.filter(**kwargs)
		
		return self
	
	# Private methods
	def _site_filter(self, for_site=None):
		"""
		Performs a query filtering only items attached to the current site
		Override using for_site parameter:
			None (default):  Use settings.SITE_ID
			List:  Multiple options using sites__in
			Integer > 0:  Use a specific value as an override
			Integer == 0:  No restriction
		"""
		params = self._params_sites(for_site)
		if params:
			return self.filter(**params)
		else:
			# If we're passed zero, this should be unrestricted,
			# so we just do nothing if for_site evals to False
			return self
	
	def _params_sites(self, for_site=None):
		"""
		Return parameters for a same-site restriction
		Can be overridden with the for_site parameter:
			None (default):  Use the value of settings.SITE_ID
			List:  Multiple values, returns the parameter sites__id__in
			Integer > 0:  Use a specific single value for sites__id
			Integer == 0:  No restriction (returns an empty dict)
		"""
		params = {}
		if for_site is None:
			# If this is None, use the current site from settings
			params['sites'] = settings.SITE_ID
		else:
			if typeutils.is_iterable(for_site):
				# Corner case: We're using a list to override this
				params['sites__in'] = for_site
			elif for_site:
				# We've been given a specific number, so use that
				# If we're passed zero, this should be unrestricted,
				# so we just do nothing if for_site evals to False
				params['sites'] = for_site
		
		return params
