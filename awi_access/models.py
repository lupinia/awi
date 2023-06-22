#	Awi Access (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	class access_code:  Temporary codes to bypass access restrictions
#	class access_control:  This is just a meta class to be extended by other models in other apps, providing access restrictions and access checks.
#	class user_meta:  User-specific settings for logged-in users.
#	
#	Helper Functions
#	def check_mature:  Checks whether mature content can be accessed by the current user.
#	def access_query:  Returns Q objects corresponding to the access level of the current request.  Example usage:  access_control.objects.filter({main condition}).filter(access_query(request))
#	=================

from datetime import timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils import dateparse
from django.utils import timezone
from django.utils.text import slugify

from awi_utils.utils import hash_sha256

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


#	Models
class access_code(models.Model):
	code = models.SlugField(max_length=255, editable=False, unique=True)
	item_type = models.CharField(max_length=40, default='unknown', editable=False)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	
	allowed_age = models.IntegerField(default=30, blank=True, help_text='The number of days for which this code should be valid.  Enter 0 for a code that does not expire.')
	desc = models.CharField(max_length=100, null=True, blank=True)
	is_valid = models.BooleanField(default=True)
	
	timestamp_post = models.DateTimeField(auto_now_add=True, verbose_name='date/time created')
	timestamp_mod = models.DateTimeField(auto_now=True, verbose_name='date/time modified')
	hits = models.IntegerField(default=0, help_text='Number of times this code has been used.')
	
	def __unicode__(self):
		if self.allowed_age:
			return '%d-day code for %s' % (self.allowed_age, self.item_type)
		else:
			return 'permanent code for %s' (self.item_type)
	
	def expiration_date(self):
		if self.allowed_age:
			return self.timestamp_post + timedelta(days=self.allowed_age)
		else:
			return False
	
	def check_code(self, check=False):
		if check and self.valid():
			if check == self.code:
				return True
			else:
				return False
		else:
			return False
	
	def valid(self):
		if not self.is_valid:
			return False
		elif self.allowed_age > 0 and self.timestamp_post + timedelta(days=self.allowed_age) < timezone.now():
			return False
		else:
			return True
	
	def record_hit(self):
		self.hits = self.hits + 1
		self.save()
	
	def save(self, *args, **kwargs):
		if self.pk and self.is_valid and not self.valid():
			self.is_valid = False
		
		if not self.code:
			hash = hash_sha256('%s|%s' % (str(timezone.now()), self.item_type))
			self.code = slugify(hash)
		
		super(access_code, self).save(*args, **kwargs)


class user_settings(models.Model):
	user = models.OneToOneField(User)
	
	mature_available = models.BooleanField(editable=False, default=False, help_text='System field:  If True, this user has provided a birthdate indicating an age >= 18 years.')
	show_mature = models.BooleanField(default=False, help_text='Check this box to display mature content.')
	age_check_date = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date of last age check.')
	
	timestamp_post = models.DateTimeField(auto_now_add=True, verbose_name='date/time created')
	timestamp_mod = models.DateTimeField(auto_now=True, verbose_name='date/time modified')
	
	def check_mature(self):
		if self.mature_available and self.show_mature:
			return (True, '')
		else:
			if self.mature_available and not self.show_mature:
				return (False, 'voluntary')
			elif self.age_check_date and not self.mature_available:
				return (False, 'denied')
			else:
				return (False, 'prompt')
	
	def __unicode__(self):
		return self.user.username


class access_control(models.Model):
	SECURITY_OPTIONS = ((0,'Public'),(1,'Logged-In Users'),(2,'Staff'))
	
	published = models.BooleanField(db_index=True, help_text='Unpublished items can only be viewed by the creator, or users with Staff privileges, regardless of Security setting.')
	featured = models.BooleanField(db_index=True, help_text='Display this item on the homepage, and at the top of the list elsewhere.')
	mature = models.BooleanField(db_index=True, help_text='Mature content can only be viewed by users who verify their age.')
	security = models.IntegerField(choices=SECURITY_OPTIONS, default=0, db_index=True, blank=True)
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	sites = models.ManyToManyField(Site, db_index=True, help_text='Sites/domains on which this item will appear.')
	access_code = models.ForeignKey(access_code, null=True, blank=True, on_delete=models.SET_NULL)
	
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
#		Return a tuple; first value is boolean, can view or not.  Second value is an error message if False, empty if True
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
	
	class Meta:
		abstract = True


