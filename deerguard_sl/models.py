#	DeerGuard SL (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.conf import settings
from django.db import models
from django.utils import timezone

class security_system(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField(unique=True)
	owner = models.ForeignKey('usertools.person', on_delete=models.PROTECT, related_name='security_systems_owned')
	grid = models.CharField(max_length=100, choices=settings.GRID_OPTIONS, help_text='Select the virtual world/"grid" for this security system.')
	
	channel_devices = models.BigIntegerField(help_text='LSL script channel for devices to send authorization commands (servers will listen on this channel).')
	channel_servers = models.BigIntegerField(help_text='LSL script channel for servers to send responses to devices (devices will listen on this channel).')
	notes = models.TextField(blank=True, null=True)
	
	system_admins = models.ManyToManyField('usertools.person', blank=True, related_name='security_systems_managed')
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')

class security_server(models.Model):
	system = models.ForeignKey(security_system, related_name='servers', on_delete=models.CASCADE)
	name = models.CharField(max_length=64)
	key = models.UUIDField()
	sim = models.ForeignKey('deerland.region', on_delete=models.PROTECT)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_sync = models.DateTimeField(blank=True, null=True, verbose_name='date/time synchronized')
	
	@property
	def is_synchronized(self):
		if self.timestamp_sync and self.timestamp_sync >= self.timestamp_mod:
			return True
		else:
			return False

class security_zone(models.Model):
	system = models.ForeignKey(security_system, related_name='zones', on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	slug = models.SlugField()
	notes = models.TextField(blank=True, null=True)
	
	auth_public = models.BooleanField(default=False, blank=True)
	auth_samegroup = models.BooleanField(default=False, blank=True)
	auth_private = models.BooleanField(default=False, blank=True)
	
	auth_users_allowed = models.ManyToManyField('usertools.person', blank=True, related_name='zones_allowed')
	auth_users_denied = models.ManyToManyField('usertools.person', blank=True, related_name='zones_denied')
	auth_groups_allowed = models.ManyToManyField('usertools.group', blank=True, related_name='zones_allowed')
	auth_groups_denied = models.ManyToManyField('usertools.group', blank=True, related_name='zones_denied')
	
	log_allowed = models.BooleanField(blank=True, default=True)
	log_denied = models.BooleanField(blank=True, default=True)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def user_allowed(self, user):
		# Given a specific user, test whether they're allowed to do the thing they're trying to do.
		# NOTE:
		#	Since we can't reliably pull a specific user's current group title,
		#	all group checks are performed within SL by the LSL security server.
		#	Therefore, this method must assume these checks have already been done, unfortunately.
		action = False
		action_code = 'UNKNOWN'
		
		if user == self.system.owner:
			# System owner can always do everything
			# In fact, the LSL scripts should know that and handle it before getting here
			action = True
			action_code = 'ALLOW_OWNER'
		elif self.auth_private:
			# If the zone is set to Private, and user is not the owner, always return False
			action = False
			action_code = 'OWNER_ONLY'
		elif self.auth_users_denied.filter(pk=user.pk).exists():
			# If the user is in the denied list, always return False
			action = False
			action_code = 'USER_BLOCKED'
		elif self.auth_public and not self.private and not self.same_group:
			# If auth_public is True, everyone can do everything, unless specifically blocked
			action = True
			action_code = 'ALLOW_ALL'
		elif self.auth_users_allowed.filter(pk=user.pk).exists():
			# If the user is in the allowed list, return True
			action = True
			action_code = 'USER_ALLOWED'
		else:
			# If no other condition has activated, return False by default
			action = False
			action_code = 'DEFAULT_DENY'
		
		if (self.log_allowed and action) or (self.log_denied and not action):
			auth_log.objects.create(zone=self, user=user, action=action, action_code=action_code)
		
		return (action, action_code)

class auth_log(models.Model):
	zone = models.ForeignKey(security_zone, related_name='logs', on_delete=models.CASCADE)
	user = models.ForeignKey('usertools.person', related_name='auth_logs', on_delete=models.CASCADE)
	action = models.BooleanField(blank=True, help_text='True if allowed, False if denied')
	action_code = models.CharField(max_length=20, default='UNKNOWN')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
