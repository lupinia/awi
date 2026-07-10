#	Dagasi - Content Security (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import User, Group
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils import dateparse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify

from awi.utils.hash import hash_sha256
from awi.utils.models import TimestampModel
from dagasi.types import status

@python_2_unicode_compatible
class user_settings(models.Model):
	# Core fields
	user = models.OneToOneField('auth.User', related_name='settings', on_delete=models.CASCADE)
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified', help_text="Timestamp showing when this item was last edited.  Automatically set with every save operation, can't be overridden.")
	
	# Content display settings
	_show_hidden = models.BooleanField(default=False, blank=True, verbose_name='list hidden?', help_text='Check this box to always display hidden content in list views.')
	
	# Mature content settings
	is_adult = models.BooleanField(editable=False, default=False, help_text='System field:  If True, this user has provided a birthdate indicating an age >= 18 years.')
	_show_mature = models.BooleanField(default=False, blank=True, verbose_name='show mature?', help_text='Check this box to display mature content.')
	age_check_date = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date of last age check.')
	
	# General content display properties and methods
	@property
	def show_hidden(self):
		"""Whether to display hidden content in list views to the current user"""
		if self._show_hidden:
			if self.user.has_perm('dagasi.list_hidden'):
				return True
			else:
				return False
		else:
			return False
	
	# Mature content properties and methods
	@property
	def show_mature(self):
		"""Whether to show mature content to the current user"""
		if self.is_adult and self._show_mature:
			return status(True, '')
		else:
			if self.is_adult and not self._show_mature:
				# This user has already passed the form and opted not to show mature content
				return status(False, 'access_mature_voluntary')
			elif self.age_check_date and not self.is_adult:
				# This user submitted the form but did not pass
				return status(False, 'access_mature_denied')
			else:
				# This user has not yet submitted the form, so show it to them
				return status(False, 'access_mature_prompt')
	
	def verify_age(self, dob):
		"""
		user_settings.verify_age(date) -> success
		
		Performs minimal necessary age verification for a logged-in user
		Always records results and cannot be repeated
		Birthdate is not recorded, it is only used in calculations
		"""
		if self.age_check_date:
			return status(False, 'already_submitted')
		
		cur = timezone.now().date()
		min_age = cur.replace(year=cur.year-18)
		
		if dob < min_age:
			self.is_adult = True
		else:
			self.is_adult = False
		
		self.age_check_date = timezone.now()
		self.save()
		return status(self.is_adult, 'form_verify')
	
	# Output
	def as_dict(self):
		"""Return various settings as a dictionary to add to session data"""
		prefs = {
			'show_mature': self.show_mature,
			'show_hidden': self.show_hidden,
		}
		return prefs
	
	# System methods and overrides
	def __str__(self):
		return self.user.username
	
	class Meta:
		default_permissions = ()
		permissions = (
			('list_hidden', 'Can enable hidden content in list views'),
			('view_cross_site', 'Can always view regardless of Sites setting'),
		)


@python_2_unicode_compatible
class blocked_ip(TimestampModel):
	address = models.GenericIPAddressField(db_index=True, unique=True)
	user_agent = models.TextField(null=True, blank=True)
	active = models.BooleanField(default=True, blank=True, db_index=True)
	notes = models.TextField(blank=True, null=True)
	
	def __str__(self):
		return self.address
	
	def save(self, *args, **kwargs):
		cache.set('blocked_ip_%s' % self.address, self.active, 60*60*24*7)
		return super(blocked_ip, self).save(*args, **kwargs)
	
	class Meta:
		verbose_name = 'blocked IP'
