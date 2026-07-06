#	Dagasi - Content Security (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import uuid
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.text import slugify

from awi.utils import types as typeutils
from awi.utils.hash import hash_sha256
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


#	Automatically build database constraints based on the current request.
#	Returns a set of Q objects that can be directly added to the parameters of a .filter() in a QuerySet.
#	Alternately, you can chain it together with your own Q objects.
#	Usage examples:
#		queryset.filter(access_query(self.request)).filter(parent__slug=self.kwargs.get('slug'))
#		queryset.filter(Q(parent__slug=self.kwargs.get('slug')) & access_query(self.request))
def access_query(request=False):
	returned_query = models.Q(sites__id = settings.SITE_ID)
	
	if request:
		if request.user.is_authenticated():
			if not request.user.is_superuser and not request.user.is_staff:
				#	Regular User
				published_query = models.Q(published = True) or models.Q(owner = request.user)
				returned_query = returned_query & models.Q(security__lt = 2) & published_query
		else:
			#	Guest
			returned_query = returned_query & models.Q(security__lt = 1) & models.Q(published = True)
		
		mature_check = check_mature(request)
		if not mature_check[0]:
			returned_query = returned_query & models.Q(mature = False)
	else:
		#	No request to check, assume least permissions.
		returned_query = returned_query & models.Q(security__lt = 1) & models.Q(published = True) & models.Q(mature = False)
	
	return returned_query


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
	published = models.BooleanField(db_index=True, help_text='Unpublished items can only be viewed by the creator, or users with Staff privileges, regardless of Security setting.')
	mature = models.BooleanField(db_index=True, help_text='Mature content can only be viewed by users who verify their age.')
	hidden = models.BooleanField(default=False, db_index=True, help_text='Omit from directory listings even if published is checked.')
	sites = models.ManyToManyField('sites.Site', db_index=True, related_name='+', help_text='Sites/domains on which this item will appear.')
	
	# Ownership and conditional access grants
	owner = models.ForeignKey('auth.User', on_delete=models.PROTECT)
	access_code = models.ForeignKey('dagasi.access_code', null=True, blank=True, on_delete=models.SET_NULL)
	
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
	
	def is_public(self):
#		Returns a tuple.  First value is boolean, indicating whether non-authenticated users can view this or not.  Second value is a list of reasons why not.
		restrictions = []
		public = True
		
		if not self.published:
			public = False
			restrictions.append('Not published')
		if self.security:
			public = False
			restrictions.append('Permissions set to %s' % self.get_security_display())
		if self.mature:
			public = False
			restrictions.append('Mature content')
		
		return (public, restrictions)
	
	# Helper method for extracting a reason for non-public status that's easier to work with programmaticly
	@property
	def restriction(self):
		ispublic = self.is_public()
		if ispublic[0]:
			return False
		else:
			if not self.published:
				return 'draft'
			elif self.security > 0:
				return 'locked'
			else:
				return 'unknown'
	
	# Quick-edit operations
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
	
	
	# System methods and overrides
	def save(self, *args, **kwargs):
		if self.security < self.ACCESS_LEVEL_MINIMUM:
			self.security = self.ACCESS_LEVEL_MINIMUM
		
		super(SecuredModel, self).save(*args, **kwargs)
	
	class Meta:
		abstract = True


# Access Codes
@python_2_unicode_compatible
class access_code(models.Model):
	code = models.SlugField(max_length=255, editable=False, unique=True)
	item_type = models.CharField(max_length=40, default='unknown', editable=False)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	desc = models.CharField(max_length=100, null=True, blank=True)
	
	allowed_age = models.PositiveSmallIntegerField(default=30, blank=True, help_text='The number of days for which this code should be valid.  Enter 0 for a code that does not expire.')
	is_valid = models.BooleanField(default=True)
	
	timestamp_post = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='date/time created')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	hits = models.PositiveIntegerField(default=0, help_text='Number of times this code has been used.')
	
	# Static calculated properties and states
	@property
	def expiration_date(self):
		"""Datetime for this code's expiration, or None if it does not expire"""
		if self.allowed_age:
			return self.timestamp_post + timedelta(days=self.allowed_age)
		else:
			return False
	
	def valid(self):
		"""Validity of this code, returns status(False) if revoked or expired"""
		if not self.is_valid:
			return False
		elif self.allowed_age > 0 and timezone.now() > self.expiration_date:
			return False
		else:
			return True
	
	
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
		self.is_valid = False
		self.save()
	
	def check_code(self, check=False):
		if check and self.valid():
			if check == self.code:
				return True
			else:
				return False
		else:
			return False
	
	
	# System methods and overrides
	def save(self, *args, **kwargs):
		if self.pk and self.is_valid and not self.valid():
			self.is_valid = False
		
		if not self.code:
			hash = hash_sha256('%s|%s' % (str(timezone.now()), self.item_type))
			self.code = slugify(hash)
		
		super(access_code, self).save(*args, **kwargs)
	
	def __str__(self):
		if self.allowed_age:
			return '%d-day code for %s' % (self.allowed_age, self.item_type)
		else:
			return 'permanent code for %s' (self.item_type)
