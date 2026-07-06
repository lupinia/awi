#	Dagasi - Content Security (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from datetime import timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth import User, Group
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils import dateparse
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
	
	# Mature content settings
	mature_available = models.BooleanField(editable=False, default=False, help_text='System field:  If True, this user has provided a birthdate indicating an age >= 18 years.')
	show_mature = models.BooleanField(default=False, help_text='Check this box to display mature content.')
	age_check_date = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date of last age check.')
	
	# Mature content properties and methods
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
	
	def __str__(self):
		return self.user.username


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
