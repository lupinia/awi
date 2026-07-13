#	Dagasi - Content Security (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.text import slugify

from awi.utils import types as typeutils
from awi.utils.hash import hash_sha256
from awi.utils.models import params_to_Q
from dagasi.types import status

#	Helper Functions
def check_mature(request=False):
	if request:
		if request.user.is_authenticated():
			if not hasattr(request.user, 'user_settings'):
				user_settings.objects.create(user=request.user)
			mature_auth_check = request.user.user_settings.check_mature()
			if mature_auth_check[0]:
				return (True, '')
			else:
				return (False, 'access_mature_%s' % mature_auth_check[1])
		
		elif request.session.get('awi_mature_denied', False):
			return (False, 'access_mature_denied')
		
		elif request.session.get('awi_mature_access', False):
			if dateparse.parse_datetime(request.session.get('awi_mature_access', False)) > timezone.now():
				return (True, '')
			else:
				return (False,'access_mature_prompt')
		
		else:
			return (False,'access_mature_prompt')
	else:
		return (False,'access_norequest')


#	A version of access_query modified for Haystack.
#	Expects a SearchQuerySet object.
#	Unpublished items should not be indexed by Haystack at all, so this assumes they won't be.
#	Because SearchQuerySets work a little differently from QuerySets, it's more reliable to use .exclude() for most of this.
#	This is also why this function adds to the SearchQuerySet chain directly, instead of returning .filter() parameters.
#	Usage example:
#		queryset = access_search(queryset, self.request)
def access_search(sqs, request=False):
	sqs = sqs.filter(sites=settings.SITE_ID)
	
	if request:
		if request.user.is_authenticated():
			if not request.user.is_superuser and not request.user.is_staff:
				# Regular User
				sqs = sqs.exclude(security__gt = 1)
		
		else:
			# Guest
			sqs = sqs.exclude(security__gt = 0)
		
		mature_check = check_mature(request)
		if not mature_check[0]:
			sqs = sqs.exclude(mature=True)
	
	else:
		# No request to check, assume least permissions.
		sqs = sqs.exclude(mature=True, security__gt=0)
	
	return sqs


# QUERYSETS AND MANAGERS
class SecuredQuerySet(models.QuerySet):
	def public(self, include_hidden=False, include_mature=False, for_site=None):
		"""
		Retrieve only content that's publicly visible
		Additional parameters for selectively overriding hidden or mature settings
		"""
		params = self._params_public(include_hidden, include_mature, for_site)
		
		return self.filter(**params)
	
	def for_user(self, user=None, include_hidden=False, include_mature=False, for_site=None):
		"""
		Retrieve only content that the specified user can view
		Additional parameters for selectively overriding hidden or mature settings
		"""
		if user and user.is_active:
			if user.is_superuser:
				# No restrictions on superusers
				return self
			else:
				# TODO: Use cache to get mature and hidden settings for current user?
				return self.filter(self._Qchain_user(user, include_hidden, include_mature, for_site))
		
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
			
			check_access_codes = request.session.get('dagasi_access_codes', [])
			if request.GET.get('access_code', False):
				if not request.GET['access_code'] in check_access_codes:
					check_access_codes.append(request.GET['access_code'])
			
			if request.user.is_authenticated():
				if check_access_codes and request.user.is_active and not request.user.is_superuser:
					# Include access codes in filter, but only if it's relevant
					return self.filter(self._Qchain_user(request.user, include_hidden=include_hidden, include_mature=include_mature) | (models.Q(access_code__in=check_access_codes) & models.Q(access_code__valid=True) & (models.Q(access_code__expiration_date__isnull=True) | models.Q(access_code__expiration_date__gt=timezone.now()))))
				else:
					return self.for_user(request.user, include_hidden=include_hidden, include_mature=include_mature)
			else:
				return self.public(include_hidden=include_hidden, include_mature=include_mature)
		
		else:
			return self.public()
	
	def created_by(self, user, include_contributors=True):
		"""
		Performs a query filtering only objects created or contributed to by the specified user.
		Pass include_contributors=False to only get the specified user's objects
		Returns queryset.none() if user does not exist
		"""
		if user:
			if include_contributors:
				return self.filter(self._Qchain_contributor(user))
			else:
				return self.filter(owner=user)
		else:
			return self.none()
	
	
	# Begin private methods
	def _params_public(self, include_hidden=False, include_mature=False, for_site=None):
		"""
		Return a dictionary of query parameters that can be passed as kwargs to a single .filter()
		Used in .public() method, separate for easier overriding
		Includes the parameters defined in _params_published()
		"""
		params = self._params_published()
		params['security__lt'] = 1
		
		# Overrides for partial restrictions
		if not include_hidden:
			params['hidden'] = False
		if not include_mature:
			params['mature'] = False
		
		# Override for site ID
		params.update(self._params_sites(for_site))
		
		return params
	
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
			params['sites__id'] = settings.SITE_ID
		else:
			if typeutils.is_iterable(for_site):
				# Corner case: We're using a list to override this
				params['sites__id__in'] = for_site
			elif for_site:
				# We've been given a specific number, so use that
				# If we're passed zero, this should be unrestricted,
				# so we just do nothing if for_site evals to False
				params['sites__id'] = for_site
		
		return params
	
	def _params_published(self, **kwargs):
		"""
		Returns a dictionary of query parameters defining what's published
		Override for content types that have additional constraints on publication status
		Additional kwargs will be appended to the output params,
		and will overwrite them if the keys are the same.
		"""
		params = {
			'published': True,
		}
		
		if kwargs:
			params.update(kwargs)
		
		return params
	
	
	def _Qchain_contributor(self, user):
		"""Return the Q objects defining whether a user is the owner or a contributor"""
		return (models.Q(owner=user) | models.Q(contributors=user))
	
	def _Qchain_user(self, user, include_hidden=False, include_mature=False, for_site=None):
		"""
		Returns the Q filter parameters for the specified user
		If user does not exists or is not active, return the public restrictions
		If user is superuser, returns an empty filter set (no restrictions)
		Else, return the following query restrictions:
			(user is owner OR user is in contributors)
			OR (security <= 2 AND groups in user groups AND is published)
			OR (security <= 1 AND is published)
		"""
		if user and user.is_active:
			if user.is_superuser:
				return models.Q()
			else:
				# Here's where things get complicated
				published_params_extra = {}
				group_params_extra = {}
				if not user.has_perm('dagasi.view_cross_site'):
					published_params_extra.update(self._params_sites(for_site))
				
				if not include_hidden:
					published_params_extra['hidden'] = False
					group_params_extra['hidden'] = False
				
				if not include_mature:
					published_params_extra['mature'] = False
					group_params_extra['mature'] = False
				
				q_objs = self._Qchain_contributor(user)
				q_objs = q_objs | (models.Q(security__lte=2) & models.Q(groups__user=user) & params_to_Q(self._params_published(group_params_extra)))
				q_objs = q_objs | (models.Q(security__lte=1) & params_to_Q(self._params_published(published_params_extra)))
				return q_objs
		
		else:
			return params_to_Q(self._params_public(include_hidden, include_mature, for_site))


class SecuredManager(models.Manager):
	@property
	def related_fieldnames(self):
		"""
		Shortcut for standard select_related field names, as a list.
		Override in child classes to include more.
		"""
		return ['owner', 'access_code', ]
	
	@property
	def prefetch_fieldnames(self):
		"""
		Shortcut for standard prefetch_related field names, as a list.
		Override in child classes to include more.
		"""
		return ['contributors', 'groups', 'sites', ]
	
	def get_queryset(self):
		return SecuredQuerySet(self.model, using=self._db).select_related(*self.related_fieldnames).prefetch_related(*self.prefetch_fieldnames)
	
	def public(self, include_hidden=False, include_mature=False):
		"""
		Retrieve only content that's publicly visible
		Additional parameters for selectively overriding hidden or mature settings
		"""
		return self.get_queryset().public(include_hidden=include_hidden, include_mature=include_mature)
	
	def for_user(self, user=None, include_hidden=False, include_mature=False):
		"""
		Retrieve only content that the specified user can view
		Additional parameters for selectively overriding hidden or mature settings
		"""
		return self.get_queryset().for_user(user=user, include_hidden=include_hidden, include_mature=include_mature)
	
	def for_request(self, request=None, force_hidden=False):
		"""
		Retrieve only content that the specified request can view, including user access
		Pass force_hidden parameter to override hidden content preferences from request.userprefs
		"""
		return self.get_queryset().for_request(request=request, force_hidden=force_hidden)
	
	def created_by(self, user=None, include_contributors=True):
		"""
		Performs a query filtering only objects created or contributed to by the specified user.
		Pass include_contributors=False to only get the specified user's objects
		Returns queryset.none() if user does not exist
		"""
		return self.get_queryset().created_by(user=user, include_contributors=include_contributors)


# MODELS
class SecuredModel(models.Model):
	"""
	Extendable base class for content-item security and authorization controls
	"""
	# Field choices constants
	ACCESS_LEVEL_OPTIONS = (
		(0, 'Public'),
		(1, 'Users'),
		(2, 'Group'),
		(3, 'Private'),
	)
	
	# Other constants
	ACCESS_LEVEL_MINIMUM = 0
	
	# Basic toggle fields
	security = models.PositiveSmallIntegerField(choices=ACCESS_LEVEL_OPTIONS, default=ACCESS_LEVEL_MINIMUM, db_index=True, blank=True)
	published = models.BooleanField(default=False, db_index=True, help_text='Unpublished items can only be viewed by the creator and contributors, or administrative users.')
	mature = models.BooleanField(default=False, db_index=True, help_text='Mature content can only be viewed by users who verify their age.')
	hidden = models.BooleanField(default=False, db_index=True, help_text='Omit from directory listings even if published is checked.')
	sites = models.ManyToManyField('sites.Site', db_index=True, related_name='+', help_text='Sites/domains on which this item will appear.')
	
	# Ownership and conditional access grants
	owner = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_owned")
	contributors = models.ManyToManyField('auth.User', db_index=True, related_name="%(app_label)s_%(class)s_contributed")
	groups = models.ManyToManyField('auth.Group', db_index=True, related_name="%(app_label)s_%(class)s_access")
	access_code = models.OneToOneField('dagasi.access_code', null=True, blank=True, on_delete=models.SET_NULL, related_name='access_to')
	
	# Helper fields
	guid = models.UUIDField(default=uuid.uuid4, unique=True)
	
	# Managers
	objects = SecuredManager()
	
	# Static calculated properties and states
	@property
	def is_published(self):
		"""Publication status, to make it easier to override with additional logic"""
		if self.published:
			return status(True)
		else:
			return status(False, 'draft')
	
	@property
	def is_public(self):
		cur_state = status(True)
		if self.hidden:
			cur_state.update(False, 'hidden')
		if self.mature:
			cur_state.update(False, 'mature')
		if self.security:
			cur_state.update(False, 'locked-%s' % self.get_security_display().lower())
		if not self.is_published:
			cur_state.update(False, self.is_published.reason)
		
		return cur_state
	
	@property
	def state(self):
		"""
		Short code indicating primary publication/security status.
		Proxy for reason field for is_public
		Used to answer the question 'if you have to pick just one restriction, which is it?'
		Possible return values, in order of precedence:
			draft (published==False)
			locked-private (security==3)
			locked-group (security==2)
			locked-users (security==1)
			mature (mature==True)
			hidden (hidden==True)
		"""
		return self.is_public.reason
	
	# Permission checks
	def can_view(self, request=False):
		"""
		Primary permission check for viewing an object
		Can check either a request, or a user
			If both are provided, request will take priority
		"""
		public_check = self.is_public()
		if public_check[0]:
			# If it's public, then can_view is assumed to be true.
			return (True,'')
		
		if not request:
			#	Fail if we can't check the request
			return (False,'access_norequest')
		
		if request.user.is_superuser:
			#	Superuser can always view
			return (True,'')
		
		# Access code validation is separate from the rest.
		if request:
			if self.access_code and self.access_code.valid():
				if request.session.get('awi_access_codes', False):
					if self.access_code.code in request.session.get('awi_access_codes', False):
						return (True, '')
				
				if request.GET.get('access_code', False):
					if self.access_code.check_code(request.GET.get('access_code', False)):
						self.access_code.record_hit()
						if not request.session.get('awi_access_codes', False):
							request.session['awi_access_codes'] = []
						request.session['awi_access_codes'].append(request.GET.get('access_code', False))
						return (True, '')
		
		# Begin normal checks.
		if (not request.user.is_staff and self.security > 1) or (not request.user.is_authenticated() and self.security > 0):
			#	If insufficient permissions, show permission error
			return (False,'access_perms')
		
		elif not self.published and (not request.user.is_staff or self.owner != request.user):
			#	If it's unpublished, object only exists if we're staff, or the author.
			return (False,'access_404')
		
		elif not self.sites.filter(pk=settings.SITE_ID).exists():
			#	If we're on the wrong site, object doesn't exist.
			return (False,'access_404')
		
		elif self.mature == True:
			#	Mature content filter.
			return check_mature(request)
		
		else:
			#	All access checks passed, show object.
			return (True,'')
	
	def can_view_user(self, user=None, check_mature=False):
		"""
		SecuredModel.can_view_user(user, check_mature=False) -> status(result, reason)
		
		Permission check for a specific user, which can be performed independently of a request
		Optionally pass check_mature=True if mature content access should be checked
			This is usually handled per-request in can_view,
			because it's very inefficient to check it here
			But it's an option when needed
		If user is not passed, this will return the results of SecuredModel.is_public
		"""
		if not user:
			# If there's no user account to check, fall back on public permissions
			access_check = self.is_public
			if access_check:
				access_check.update(self.same_site, 'access_404')
			else:
				access_check.reason = 'access_norequest'
			return access_check
		
		# If we made it this far, we have a user to check
		if user.is_superuser or user.pk in self.contributors_ids:
			# Superuser always has full permission
			# Owner and contributors can always view
			return status(True)
		
		elif self.security > 2 or not self.published:
			# If item is unpublished and user is not owner, contributor, or superuser, item does not exist
			# Private items are only available to owner, contributors, and superuser
			return status(False, 'access_404')
		
		elif not self.same_site and not user.has_perm('dagasi.view_cross_site'):
			# If current object isn't attached to the current site,
			# it doesn't technically exist to the current user,
			# unless they have the view_cross_site permission
			return status(False, 'access_404')
		
		elif self.security == 2:
			# Group access mode
			if user.groups.filter(pk__in=self.groups_ids):
				return status(True)
			else:
				return status(False, 'access_perms')
		
		elif check_mature and self.mature:
			# This is an inefficient way to check the per-user mature settings
			# We'll default to assuming this is checked elsewhere
			return user.settings.show_mature
		
		else:
			# No reason to deny them here!
			return status(True)
	
	def can_edit(self, request=False, perm_check=''):
#		Return a tuple; first value is boolean, can edit or not.  Second value is an error message if False, empty if True
		if not request:
			return (False,'access_norequest')				#	Fail if we can't check anything
		else:
			access_check = self.can_view(request)
			if request.user.is_superuser:
				return (True,'')				#	Superuser can always edit.
			elif not access_check[0]:
				return access_check				# If we can't view, we can't edit.
			elif perm_check and not request.user.has_perm(perm_check):
				return (False,'access_perms')
			elif self.owner is not request.user:
				return (False,'access_notowner')	# If we're not a superuser, and this isn't our item, we can't edit it.
			else:
				return (True,'')				#	All access checks passed, edit object.
	
	# Editing operations
	def quick_edit(self, field, value, refresh=True):
		success = self.__class__.objects.filter(pk=self.pk).update(**{field:value})
		if success and refresh:
			self.refresh_from_db()
		
		return success
	
	def get_url_domain(self, request=None):
		"""
		Get a domain name for building canonical URLs.
		Optionally pass the request object to use the same hostname.
		"""
		if request:
			domain = request.get_host()
		else:
			domain_cache_key = 'model_urldomain.%s.%d' % (self.__class__.__name__, self.pk)
			domain = cache.get(domain_cache_key)
			if domain is None:
				primary_site = self.sites.all().order_by('pk').first()
				if not primary_site:
					primary_site = get_current_site()
				
				domain = primary_site.domain
				if not domain.startswith('www.'):
					domain = 'www.%s' % domain
				
				cache.set(domain_cache_key, domain, 60*60*24*7)
		
		return domain
	
	# Access code operations
	def access_code_check(self, check, first_hit=False):
		"""
		SecuredModel.access_code_check(str or list, first_hit=False) -> status(result, reason) or None
		
		Tests whether the specified code(s) are valid and grant access to this object
		If first_hit is True, the code's hit counter will be incremented
		Returns None if this object has no access code, because that's neither a pass nor fail
		"""
		if not check:
			return status(False, 'access_code_nocheck')
		
		if not self.access_code:
			# Weird corner-case where this neither passes nor fails because there's no code
			# Forcing this to be handled uniquely by returning None
			return None
		
		if typeutils.is_string(check):
			# Single-check mode
			return self.access_code.check(check, first_hit)
		
		elif typeutils.is_iterable(check):
			# Assuming this is a list
			# We have to do a little extra work ourselves for this one
			# This is also more likely to be ambiguous
			check_result = self.access_code.is_valid
			if not check_result:
				return check_result
			elif self.access_code.code in check:
				if first_hit:
					# This makes no sense, but sure I guess
					self.access_code.record_hit()
				return status(True)
			else:
				return status(False, 'access_code_nomatch')
		
		else:
			return status(False, 'access_code_invalid')
	
	def create_code(self, age=30, desc=None, request=False):
		if not self.is_public()[0]:
			if request:
				if request.user.is_authenticated() and request.user == self.owner:
					self.access_code = access_code.objects.create(item_type=self.__class__.__name__, allowed_age=age, desc=desc, owner=request.user)
					self.save()
					return True
				else:
					return False
			else:
				return False
		else:
			return False
	
	# Caching
	@property
	def objcache_id(self):
		"""Unique prefix to use for this object in the cache"""
		if self.guid:
			return 'obj.%s' % self.guid
		else:
			return None
	
	@property
	def objcache_keys(self):
		"""Retrieve a list of keys to clear when resetting the cache for this object"""
		if self.objcache_id is None:
			return None
		
		keylist = [
			'siteid_list',
			'contributorid_list',
			'groupid_list',
		]
		return [self.cache_key(x) for x in keylist]
	
	def cache_key(self, key):
		"""Return a prefixed version of the given key"""
		if self.objcache_id is None:
			return None
		else:
			return '%s.%s' % (self.objcache_id, key)
	
	def cache_clear(self):
		"""
		Clear the parameter cache for this object
		Relies on the list contained in .objcache_keys
		"""
		if self.objcache_keys:
			cache.delete_many(self.objcache_keys)
	
	def cache_get(self, key, fallback=None):
		"""
		Proxy for cache.get(), with a prefixed key unique to this object
		Include a fallback value other than None to get a default
		"""
		return cache.get(self.cache_key(key), fallback)
	
	def cache_set(self, key, value, timeout=None):
		"""
		Proxy for cache.set(), with a prefixed key unique to this object
		Defaults to permanent, set timeout for an expiration time
		"""
		return cache.set(self.cache_key(key), value, timeout)
	
	@cached_property
	def sites_ids(self):
		"""Cached IDs list for the sites this object is part of"""
		siteids = self.cache_get('siteid_list')
		if siteids is None:
			siteids = list(self.sites.all().values_list('pk', flat=True))
			self.cache_set('siteid_list', siteids)
			return siteids
	
	@cached_property
	def same_site(self):
		"""Cached check on whether the current site matches the current object's sites"""
		siteids = self.sites_ids
		return settings.SITE_ID in siteids
	
	@cached_property
	def contributors_ids(self):
		"""Cached list of contributor users, with owner included"""
		contrib_ids = self.cache_get('contributorid_list')
		if contrib_ids is None:
			contrib_ids = list(self.contributors.all().values_list('pk', flat=True))
			contrib_ids.append(self.owner_id)
			self.cache_set('contributorid_list', contrib_ids)
			return contrib_ids
	
	@cached_property
	def groups_ids(self):
		"""Cached list of groups this object is set to"""
		groupids = self.cache_get('groupid_list')
		if groupids is None:
			groupids = list(self.groups.all().values_list('pk', flat=True))
			self.cache_set('groupid_list', groupids)
			return groupids
	
	
	# System methods and overrides
	def save(self, *args, **kwargs):
		if self.security < self.ACCESS_LEVEL_MINIMUM:
			self.security = self.ACCESS_LEVEL_MINIMUM
		
		self.cache_clear()
		super(SecuredModel, self).save(*args, **kwargs)
	
	class Meta:
		abstract = True
		default_permissions = ('add', 'change', 'change_contrib', 'change_group', 'delete',)


# Access Codes
@python_2_unicode_compatible
class access_code(models.Model):
	code = models.SlugField(max_length=255, editable=False, unique=True)
	item_type = models.CharField(max_length=40, default='unknown', editable=False)
	owner = models.ForeignKey('auth.User', related_name='+', on_delete=models.CASCADE)
	desc = models.CharField(max_length=100, null=True, blank=True)
	
	allowed_age = models.PositiveSmallIntegerField(default=30, blank=True, help_text='The number of days for which this code should be valid.  Enter 0 for a code that does not expire.')
	valid = models.BooleanField(default=True)
	
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, editable=False, verbose_name='date/time created')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	expiration_date = models.DateTimeField(null=True, db_index=True, editable=False, verbose_name='date/time expires')
	hits = models.PositiveIntegerField(default=0, help_text='Number of times this code has been used.')
	
	# Static calculated properties and states
	@property
	def is_valid(self):
		"""Validity of this code, returns status(False) if revoked or expired"""
		if not self.valid:
			return status(False, 'access_code_revoked')
		elif self.expiration_date and timezone.now() > self.expiration_date:
			return status(False, 'access_code_expired')
		else:
			return status(True)
	
	
	# Code operation methods
	def record_hit(self):
		"""Increment the hit counter for this code.  Performs a .save()"""
		self.hits = self.hits + 1
		self.save()
	
	def revoke(self):
		"""
		Set this code to invalid status.  Performs a .save()
		Cannot be undone.
		Counterpart operation is issuing a code, which is performed from the object the code is for
		"""
		self.valid = False
		self.save()
	
	def check(self, raw_input=None, first_hit=False):
		"""
		access_code.check
		Check whether a specified code is correct, if this code is valid
		Returns status(result, reason)
		Automatically records a hit on success
		"""
		if not self.is_valid:
			return self.is_valid
		elif not raw_input:
			return status(False, 'access_code_nocheck')
		elif raw_input == self.code:
			if first_hit:
				self.record_hit()
			return status(True)
		else:
			return status(False, 'access_code_invalid')
	
	
	# System methods and overrides
	def save(self, *args, **kwargs):
		if self.allowed_age:
			self.expiration_date = self.timestamp_post + timedelta(days=self.allowed_age)
		else:
			self.expiration_date = None
		
		if self.pk and self.valid and not self.is_valid:
			# If this is an edit instead of a create,
			# and it's set to valid,
			# and it's expired,
			# perform a revoke action
			self.valid = False
		
		if not self.code:
			if not self.timestamp_post:
				# Make sure this is set for code generation
				self.timestamp_post = timezone.now()
			
			hash = hash_sha256('%s|%s|%s' % (str(self.timestamp_post), uuid.uuid4(), self.item_type))
			self.code = slugify(hash)
		
		super(access_code, self).save(*args, **kwargs)
	
	def __str__(self):
		if self.allowed_age:
			return '%d-day code for %s' % (self.allowed_age, self.item_type)
		else:
			return 'permanent code for %s' (self.item_type)
	
	class Meta:
		default_permissions = ()
