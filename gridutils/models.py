#	GridUtils - Virtual World Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import uuid

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from awi_utils.utils import rand_int_list
from gridutils.utils import (
	device_type_choices,
	location_model,
	coords_to_square,
	square_to_coords,
	psv_hash,
	psv_hash256,
	verify_sl_name,
)

#	===========
#	Basics
class grid(models.Model):
	name = models.CharField(max_length=64)
	slug = models.SlugField(max_length=64, unique=True)
	
	def __unicode__(self):
		return self.name


#	===========
#	Users and Accounts
class name_history(models.Model):
	profile = models.ForeignKey('avatar', related_name='past_names')
	
	grid_name_first = models.CharField(max_length=50)
	grid_name_last = models.CharField(max_length=50)
	grid_username = models.CharField(max_length=100)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	@property
	def grid_name(self):
		return '%s %s' % (self.grid_name_first, self.grid_name_last)
	
	def __unicode__(self):
		return self.grid_username
		#return '%s (Profile: %d)' % (self.grid_name, self.profile.pk)

class avatar(models.Model):
	account = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='grid_avatars')
	key = models.UUIDField(db_index=True, help_text=mark_safe('The unique identifier for this user.  <a href="http://wiki.secondlife.com/wiki/Category:LSL_Key" target="_BLANK">More info</a>.'))
	grid = models.ForeignKey(grid, on_delete=models.PROTECT, help_text='Select the virtual world/"grid" for this user.')
	active = models.BooleanField(blank=True, default=True, db_index=True, help_text='If unchecked, user no longer exists.')
	primary_for_account = models.BooleanField(blank=True, default=True, db_index=True)
	allow_gridlogin = models.BooleanField(blank=True, default=True, db_index=True)
	
	grid_name_first = models.CharField(max_length=50, blank=True, editable=False)
	grid_name_last = models.CharField(max_length=50, blank=True, editable=False)
	grid_username = models.CharField(max_length=100) #TODO: Validator!
	grid_username_cur = models.CharField(max_length=100, editable=False)
	display_name = models.CharField(max_length=250, blank=True)
	grid_username_verified = models.BooleanField(default=True, editable=False)
	
	notes = models.TextField(blank=True, null=True)
	icon_key = models.UUIDField(blank=True, null=True)
	
	web_publish = models.BooleanField(blank=True, default=True)
	is_bot = models.BooleanField(blank=True, default=False)
	is_mature = models.BooleanField(blank=True, default=False)
	grid_employee = models.BooleanField(blank=True, default=False)
	grid_verified = models.BooleanField(blank=True, default=False)
	grid_paid = models.BooleanField(blank=True, default=False)
	
	profile_text = models.TextField(blank=True, null=True)
	profile_firstlife = models.TextField(blank=True, null=True)
	profile_url = models.URLField(max_length=250, blank=True, null=True)
	profile_languages = models.CharField(max_length=250, blank=True, null=True)
	profile_skills = models.CharField(max_length=250, blank=True, null=True)
	profile_wants = models.CharField(max_length=250, blank=True, null=True)
	
	wantto_build = models.BooleanField(blank=True, default=False)
	wantto_explore = models.BooleanField(blank=True, default=False)
	wantto_meet = models.BooleanField(blank=True, default=False)
	wantto_group = models.BooleanField(blank=True, default=False)
	wantto_buy = models.BooleanField(blank=True, default=False)
	wantto_sell = models.BooleanField(blank=True, default=False)
	wantto_work = models.BooleanField(blank=True, default=False)
	wantto_hire = models.BooleanField(blank=True, default=False)
	
	skills_textures = models.BooleanField(blank=True, default=False)
	skills_architecture = models.BooleanField(blank=True, default=False)
	skills_events = models.BooleanField(blank=True, default=False)
	skills_modeling = models.BooleanField(blank=True, default=False)
	skills_scripting = models.BooleanField(blank=True, default=False)
	skills_characters = models.BooleanField(blank=True, default=False)
	
	date_gridcreate = models.DateField(blank=True, null=True, verbose_name='account creation date')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_namechange = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last name change')
	timestamp_sync = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last sync')
	
	@property
	def grid_name(self):
		return '%s %s' % (self.grid_name_first, self.grid_name_last)
	
	@property
	def name(self):
		if self.display_name:
			return self.display_name
		else:
			return self.grid_name
	
	@property
	def key_str(self):
		return str(self.key)
	
	@property
	def icon_key_str(self):
		if self.icon_key:
			return str(self.icon_key)
		else:
			return None
	
	@property
	def allow_weblogin(self):
		if self.account:
			if self.account.is_active and self.account.has_usable_password():
				# This will need to change if/when I implement an external SSO system
				return True
			else:
				return False
		else:
			return False
	
	def normalize_names(self):
		return_name_first = ''
		return_name_last = ''
		return_username = ''
		
		if ' ' in self.grid_username:
			# Grid username is a standard ("legacy") name, in the format of "Firstname Lastname"
			# We can reasonably assume that the capitalization on the first name is correct
			# Last name should be normalized with .capitalize(), which we'll do for all of them
			# After parsing, username should be normalized to "firstname.lastname".lower()
			return_name_first, return_name_last = self.grid_username.split(' ', 1)
			return_username = self.grid_username.replace(' ', '.')
		
		elif '.' in self.grid_username:
			# Grid username is a new-style name with both a first name and a last name
			# Preserve capitalization if possible, but it's probably all lowercase
			return_name_first, return_name_last = self.grid_username.split('.', 1)
			return_username = self.grid_username
		
		else:
			# Grid username is a new-style name with no last name
			# Therefore, last name should be "Resident"
			return_name_first = self.grid_username
			return_name_last = 'Resident'
			return_username = self.grid_username
		
		return (return_name_first, return_name_last.capitalize(), return_username.lower())
	
	def save(self, *args, **kwargs):
		if self.pk:
			# We're editing an object that already exists
			# Check for changes to the username, and update if necessary
			if self.grid_username.lower() != self.grid_username_cur.lower():
				name_verified, verify_status = verify_sl_name(self, self.grid_username)
				if name_verified is not False:
					if name_verified or verify_status == 'wrong_grid':
						self.grid_username_verified = True
					else:
						self.grid_username_verified = False
					
					name_history.objects.create(profile=self, grid_username=self.grid_username_cur, grid_name_first=self.grid_name_first, grid_name_last=self.grid_name_last)
					self.grid_name_first, self.grid_name_last, self.grid_username = self.normalize_names()
					self.grid_username_cur = self.grid_username
					self.timestamp_namechange = timezone.now()
				
				else:
					# Name verification through the API was successful, but returned incorrect results
					raise ValidationError('SL username validation failed')
		
		else:
			# This is a new entry, gotta do some cleanup
			self.grid_name_first, self.grid_name_last, self.grid_username = self.normalize_names()
			self.grid_username_cur = self.grid_username
			if not self.display_name:
				self.display_name = self.grid_name
		
		super(avatar, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return '%s (%s)' % (self.display_name, self.grid_username)
	
	class Meta:
		unique_together = (('key', 'grid'),)


#	===========
#	Groups
class group(models.Model):
	name = models.CharField(max_length=40)
	slug = models.SlugField(max_length=60, unique=True)
	key = models.UUIDField(db_index=True)
	grid = models.ForeignKey(grid, on_delete=models.PROTECT, help_text='Select the virtual world/"grid" for this group.')
	active = models.BooleanField(blank=True, default=True, db_index=True, help_text='If unchecked, group no longer exists.')
	
	founder = models.ForeignKey(avatar, on_delete=models.SET_NULL, blank=True, null=True, related_name='groups_founded')
	notes = models.TextField(blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	icon_key = models.UUIDField(blank=True, null=True)
	
	is_public = models.BooleanField(blank=True, default=False, help_text='If unchecked, group is not visible in public search.')
	is_open = models.BooleanField(blank=True, default=False, help_text='If unchecked, users cannot join directly, they must be invited.')
	is_mature = models.BooleanField(blank=True, default=False)
	member_count = models.PositiveIntegerField(blank=True, default=0)
	signup_fee = models.PositiveIntegerField(blank=True, default=0)
	data_incomplete = models.BooleanField(editable=False, default=False, db_index=True, help_text='If True, group was created without knowing its name.')
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_sync = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last sync')
	
	@property
	def key_str(self):
		return str(self.key)
	
	@property
	def icon_key_str(self):
		if self.icon_key:
			return str(self.icon_key)
		else:
			return None
	
	def __unicode__(self):
		return 'Group: %s (%s)' % (self.name, self.grid.name)
	
	def save(self, *args, **kwargs):
		if self.data_incomplete:
			if not self.name:
				self.name = '__unknown'
			if not self.slug or self.slug.startswith('--unknown-'):
				if self.pk:
					self.slug = '--unknown-%d' % self.pk
				else:
					self.slug = '--unknown-%d' % (group.objects.all().count() + 1)
		else:
			if not self.slug:
				self.slug = slugify(self.name)
		super(group, self).save(*args, **kwargs)
	
	class Meta:
		unique_together = (('key', 'grid'),)

class group_role(models.Model):
	role_name = models.CharField(max_length=40, blank=True, null=True, verbose_name='name')
	role_title = models.CharField(max_length=40, blank=True, null=True, verbose_name='title')
	key = models.UUIDField(blank=True, null=True)
	parent = models.ForeignKey(group, on_delete=models.PROTECT, related_name='roles')
	
	is_everyone = models.BooleanField(blank=True, default=False)
	is_owner = models.BooleanField(blank=True, default=False)
	description = models.TextField(null=True, blank=True)
	members = models.ManyToManyField(avatar, related_name='group_roles', blank=True)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_sync = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last sync')
	
	@property
	def title(self):
		if self.role_title:
			return self.role_title
		elif self.is_everyone:
			return "Member"
		elif self.is_owner:
			return "Owner"
		else:
			return None
	
	@property
	def name(self):
		if self.role_name:
			return self.role_name
		elif self.is_everyone:
			return "Everyone"
		elif self.is_owner:
			return "Owner"
		elif self.role_title:
			return self.title
		else:
			return "Unnamed Role"
	
	def __unicode__(self):
		return '%s: %s' % (self.parent.name, self.name)
	
	@property
	def key_str(self):
		return str(self.key)


#	===========
#	Land
class estate(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	grid = models.ForeignKey(grid, on_delete=models.PROTECT, help_text='Select the virtual world/"grid" for this estate and its regions.')
	grid_estate_id = models.IntegerField(default=0, help_text='Estate ID used within the grid', blank=True, null=True)
	owner = models.ForeignKey(avatar, on_delete=models.SET_NULL, null=True, blank=True)
	
	description = models.TextField(blank=True, null=True)
	covenant = models.TextField(blank=True, null=True)
	is_mainland = models.BooleanField(blank=True, default=False)
	is_rental = models.BooleanField(blank=True, default=False)
	default_estate = models.BooleanField(blank=True, default=False, help_text='If True, this estate is the "catch-all" for regions in its grid that do not have an estate defined at creation time.')
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_sync = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last sync')
	
	def __unicode__(self):
		return '%s (%s)' % (self.name, self.grid.name)
	
	class Meta:
		unique_together = (('grid_estate_id', 'grid'),)

class region(location_model):
	SIM_STATUS_OPTIONS = (
		('up','Running'),
		('down','Offline'),
		('starting','Starting Up'),
		('stopping','Shutting Down'),
		('crashed','Crashed'),
		('unknown','Unknown'),
	)
	
	RATING_OPTIONS = (
		('PG', 'General'),
		('MATURE', 'Moderate'),
		('ADULT', 'Adult'),
		('UNKNOWN', 'Unknown'),
	)
	
	name = models.CharField(max_length=64)
	slug = models.CharField(max_length=64, unique=True)
	estate = models.ForeignKey(estate, on_delete=models.PROTECT)
	status = models.CharField(max_length=10, choices=SIM_STATUS_OPTIONS, default='unknown')
	active = models.BooleanField(blank=True, default=True, db_index=True, help_text='If unchecked, region no longer exists.')
	
	notes = models.TextField(blank=True, null=True)
	map_image = models.ImageField(upload_to='regions', null=True, blank=True)
	
	rating = models.CharField(max_length=10, choices=RATING_OPTIONS, default='UNKNOWN')
	region_type = models.CharField(max_length=255, default='Unknown')
	data_gridpos_x = models.IntegerField(null=True, blank=True, verbose_name='grid location (x)')
	data_gridpos_y = models.IntegerField(null=True, blank=True, verbose_name='grid location (y)')
	
	hostname = models.TextField(null=True, blank=True)
	release_channel_reported = models.CharField(max_length=255, null=True, blank=True)
	release_channel_override = models.CharField(max_length=255, null=True, blank=True)
	release_version = models.CharField(max_length=255, null=True, blank=True)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_sync = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last sync')
	timestamp_restart = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last restart')
	
	@property
	def slurl(self):
		return self.location_slurl(self)
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if not self.location_x and not self.location_y:
			self.location_x = 128
			self.location_y = 128
		if not self.slug:
			self.slug = slugify(self.name)
		super(region, self).save(*args, **kwargs)
	
	class Meta:
		unique_together = (('name', 'estate'),)

class parcel(location_model):
	TELEPORT_OPTIONS = (
		('None', 'Blocked'),
		('LandingPoint', 'Landing Point'),
		('Direct', 'Anywhere'),
	)
	
	region = models.ForeignKey(region, on_delete=models.CASCADE, related_name='parcels')
	name = models.CharField(max_length=200, blank=True, null=True)
	key = models.UUIDField(blank=True, null=True)
	active = models.BooleanField(blank=True, default=True, db_index=True, help_text='If unchecked, parcel no longer exists.')
	settings_known = models.BooleanField(default=False, blank=True, help_text='If unchecked, parcel settings/details have not been collected')
	
	owner_account = models.ForeignKey(avatar, on_delete=models.SET_NULL, null=True, blank=True, related_name='parcels_owned')
	group = models.ForeignKey(group, on_delete=models.SET_NULL, null=True, blank=True, related_name='parcels_owned')
	group_owned = models.BooleanField(default=False, blank=True)
	rental = models.BooleanField(blank=True, default=False)
	
	# Should this be entirely dynamic?
	size = models.PositiveIntegerField(blank=True, default=0)
	border_data = JSONField(blank=True, null=True)
	border_overlay = models.ImageField(upload_to='parcel_shapes', null=True, blank=True)
	
	description = models.TextField(blank=True, null=True)
	notes = models.TextField(blank=True, null=True)
	
	autoreturn_time = models.PositiveIntegerField(blank=True, default=0)
	prim_limit = models.PositiveIntegerField(blank=True, default=0)
	prims_used = models.PositiveIntegerField(blank=True, default=0)
	
	can_terraform = models.BooleanField(blank=True, default=False)
	can_fly = models.BooleanField(blank=True, default=False)
	can_build_all = models.BooleanField(blank=True, default=False)
	can_build_group = models.BooleanField(blank=True, default=False)
	obj_entry_all = models.BooleanField(blank=True, default=False)
	obj_entry_group = models.BooleanField(blank=True, default=False)
	scripts_all = models.BooleanField(blank=True, default=False)
	scripts_group = models.BooleanField(blank=True, default=False)
	
	is_safe = models.BooleanField(blank=True, default=False)
	no_push = models.BooleanField(blank=True, default=False)
	public_search = models.BooleanField(blank=True, default=False)
	privacy_disabled = models.BooleanField(blank=True, default=False) # SL obnoxiously treats this field as a double-negative
	higher_rating = models.BooleanField(blank=True, default=False)
	public_search_type = models.CharField(max_length=100, blank=True, null=True)
	landing_type = models.CharField(max_length=15, choices=TELEPORT_OPTIONS, default='Direct')
	
	music_url = models.ForeignKey('parcel_stream', blank=True, null=True, on_delete=models.SET_NULL)
	sound_range_limit = models.BooleanField(blank=True, default=False)
	sounds_all = models.BooleanField(blank=True, default=False)
	sounds_group = models.BooleanField(blank=True, default=False)
	voice = models.BooleanField(blank=True, default=False)
	voice_range_limit = models.BooleanField(blank=True, default=False)
	
	access_public = models.BooleanField(blank=True, default=False)
	access_adult = models.BooleanField(blank=True, default=False)
	access_payment = models.BooleanField(blank=True, default=False)
	access_group = models.BooleanField(blank=True, default=False)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_sync = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last sync')
	
	def get_owner(self):
		return_type = 'unknown'
		return_obj = None
		if self.group_owned:
			return_obj = self.group
			return_type = 'group'
		else:
			return_type = 'group'
			return_obj = self.owner_account
		
		return (return_type, return_obj)
	
	@property
	def key_str(self):
		return str(self.key)
	
	@property
	def owner(self):
		return self.get_owner()[1]
	
	@property
	def owner_type(self):
		return self.get_owner()[0]
	
	def __unicode__(self):
		return self.name

class parcel_stream(models.Model):
	name = models.CharField(max_length=255, blank=True, null=True)
	url = models.URLField(max_length=1024)
	owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='music_streams')
	
	shared = models.BooleanField(blank=True, default=False, db_index=True)
	active = models.BooleanField(blank=True, default=True, db_index=True, help_text='If unchecked, stream URL no longer exists.')
	healthy = models.BooleanField(blank=True, default=True, db_index=True)
	managed = models.BooleanField(blank=True, default=False)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	@property
	def title(self):
		if self.name:
			return self.name
		else:
			return 'Untitled Stream %d' % self.pk
	
	def __unicode__(self):
		return self.title

class parcel_borders(models.Model):
	region = models.ForeignKey(region, on_delete=models.CASCADE, related_name='parcel_borders')
	parcel = models.OneToOneField(parcel, on_delete=models.CASCADE, related_name='borders')
	overlay = models.ImageField(upload_to='parcel_shapes', null=True, blank=True)
	border_data = JSONField(blank=True, null=True, default=dict)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_sync = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last sync')
	
	@property
	def squares(self):
		return self.border_data.get('raw', [])
	
	@property
	def area(self):
		return len(self.squares)*16
	
	@property
	def center(self):
		all_squares = self.squares
		target_square = 0
		
		if len(all_squares) == 0:
			return [-1, -1]
		elif len(all_squares) < 3:
			target_square = all_squares[0]
		else:
			target_square = all_squares[int(len(all_squares)/2)]
		
		return square_to_coords(target_square)
	
	def contains_square(self, target=0):
		if target in self.squares:
			return True
		else:
			return False
	
	def contains_coordinates(self, x, y, z=0):
		target = coords_to_square(x, y)
		return self.contains_square(target)
	
	def __unicode__(self):
		return '%s Borders (Parcel %d)' % (self.region.name, self.parcel.pk)

class location(location_model):
	name = models.CharField(max_length=200, blank=True, null=True)
	slug = models.SlugField(max_length=100, unique=True)
	
	region = models.ForeignKey('region', on_delete=models.SET_NULL, blank=True, null=True)
	active = models.BooleanField(blank=True, default=True, db_index=True, help_text='If unchecked, location no longer exists.')
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	app = models.CharField(max_length=40, default='unknown', db_index=True, help_text='System field:  Indicates which app this location belongs to.')
	type = models.CharField(max_length=40, default='unknown', db_index=True, help_text='System field:  Indicates which model this location is.')
	
	@property
	def valid(self):
		if self.region:
			return True
		else:
			return False
	
	def __unicode__(self):
		if self.name:
			return self.name
		else:
			return self.get_location_text(self.region)
	
	def save(self, *args, **kwargs):
		if not self.pk:
			self.app = self.__class__
			self.type = self.__class__.__name__
		super(location, self).save(*args, **kwargs)


#	===========
#	Objects

#	Parent class for in-world objects that need to communicate with the server's API
#	All other models representing different types of objects should subclass this model.
#	Be sure to also add them to settings.DEVICE_SETTINGS
class device(location_model):
	name = models.CharField(max_length=64)
	key = models.UUIDField(db_index=True)
	region = models.ForeignKey(region, on_delete=models.PROTECT, related_name='devices_hosted')
	active = models.BooleanField(blank=True, default=True, db_index=True, help_text='If unchecked, device has been disabled or deleted.')
	notes = models.TextField(blank=True, null=True)
	
	owner_account = models.ForeignKey(avatar, on_delete=models.PROTECT, related_name='devices_owned')
	group = models.ForeignKey(group, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices_owned')
	group_owned = models.BooleanField(default=False, blank=True)
	is_attached = models.BooleanField(default=False, blank=True, verbose_name='attached', help_text='If checked, this device will be excluded from location checks.  NOTE:  This value has no effect unless wearable_allowed is enabled for this object type in settings.')
	
	auth_key_hash = models.TextField(blank=True, null=True, editable=False)
	authorization = models.ForeignKey('device_authorization_token', on_delete=models.PROTECT, related_name='devices')
	
	remote_url = models.URLField(max_length=255, blank=True, null=True)
	remote_url_valid = models.BooleanField(default=False, editable=False)
	remote_url_key = models.UUIDField(blank=True, null=True, editable=False)
	
	init_start = models.BooleanField(default=False, editable=False, db_index=True, help_text="System field:  If true, the automated initialization steps have been completed successfully.")
	init_ready = models.BooleanField(default=False, editable=False, db_index=True, help_text="System field:  If true, this device is fully authenticated and ready for use.")
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_sync = models.DateTimeField(blank=True, null=True, verbose_name='date/time synchronized')
	timestamp_authkey = models.DateTimeField(blank=True, null=True, verbose_name='date/time auth key assigned')
	
	app = models.CharField(max_length=40, default='unknown', db_index=True, help_text='System field:  Indicates which app this device belongs to.')
	type = models.CharField(max_length=40, default='unknown', db_index=True, help_text='System field:  Indicates which model this device is.')
	
	#	Properties
	@property
	def model_path(self):
		return '%s.%s' % (self.app, self.type)
	
	@property
	def key_str(self):
		return str(self.key)
	
	@property
	def remote_url_key_str(self):
		return str(self.remote_url_key)
	
	@property
	def is_synchronized(self):
		if self.timestamp_sync and self.timestamp_sync >= self.timestamp_mod:
			return True
		else:
			return False
	
	@property
	def owner(self):
		return self.get_owner()[1]
	
	@property
	def owner_type(self):
		return self.get_owner()[0]
	
	@property
	def auth_key_expired(self):
		if self.timestamp_authkey:
			if timezone.now() > self.timestamp_authkey + timedelta(days=self.auth_key_maxage):
				return True
			else:
				return False
		else:
			return False
	
	@property
	def init_status(self):
		# Returns a tuple; first value is boolean (true if initialization is done)
		# Possible return values:
		#	unknown:  Something went wrong
		#	new:  Initialization not yet complete
		#	revoked:  App authorization was revoked
		#	disabled:  Device manually set to "inactive"
		#	denied:  Web confirmation was denied or expired
		#	wait_approval:  Waiting for web confirmation
		#	wait_approved:  Waiting for the device to reconnect after web confirmation
		#	ready:  Only accompanies a True response
		status = False
		code = 'unknown'
		
		if not self.active:
			status = False
			code = 'disabled'
		elif not self.authorization.active:
			status = False
			code = 'revoked'
		elif not self.authorization.parent.check_avatar(self.owner_account.key):
			status = False
			code = 'revoked'
		elif not self.init_start:
			status = False
			code = 'new'
		elif self.confirm_new and not self.init_ready:
			# Ok, the automated handshake is done, but we're still not ready.
			# Let's find out why!
			approval_request = self.get_approval_request()
			if approval_request:
				if approval_request.is_approved:
					status = False
					code = 'wait_approved'
				elif approval_request.is_open:
					status = False
					code = 'wait_approval'
				else:
					status = False
					code = 'denied'
			else:
				# Not sure how you got here, but you're probably checking this before the approval request has been sent.
				status = False
				code = 'wait_approval'
		elif self.init_start and self.init_ready and self.active and self.auth_key_hash:
			status = True
			code = 'ready'
		
		return (status, code)
	
	@property
	def health_color(self):
		# Possible return values:
		#	blue:  There have been server-side changes that are not yet reflected 
		#	green:  Everything is fine
		#	yellow:  Last sync has not occurred recently, or approval is pending
		#	orange:  Device requires remote URL, but current URL is invalid.
		#	red:  Last sync is older than maximum auth key age, or some other auth issue
		#	grey:  Device has been disabled or deleted
		if self.active:
			init_ready, init_code = self.init_status
			if init_ready:
				if not self.is_synchronized:
					return 'blue'
				elif timezone.now() > self.timestamp_sync + timedelta(days=self.auth_key_maxage):
					return 'red'
				elif self.require_url and not self.remote_url_valid:
					return 'orange'
				elif timezone.now() > self.timestamp_sync + timedelta(days=self.sync_age_yellow):
					return 'yellow'
				else:
					return 'green'
			else:
				if init_code == 'wait_approval' or init_code == 'wait_approved':
					return 'yellow'
				else:
					return 'red'
		else:
			return 'grey'
	
	
	#	Settings per-app/per-model
	@property
	def model_settings(self):
		return settings.DEVICE_SETTINGS.get(self.model_path, settings.DEVICE_SETTINGS['gridutils.device'])
	
	@property
	def confirm_new(self):
		return self.model_settings['confirm_new']
	
	@property
	def limit_duplicates(self):
		return self.model_settings['limit_duplicates']
	
	@property
	def limit_move(self):
		return self.model_settings['limit_move']
	
	@property
	def require_url(self):
		return self.model_settings['require_url']
	
	@property
	def wearable_allowed(self):
		return self.model_settings['wearable_allowed']
	
	@property
	def attached(self):
		if self.wearable_allowed and self.is_attached:
			return True
		else:
			return False
	
	@property
	def auth_key_maxage(self):
		return self.model_settings['auth_key_maxage']
	
	@property
	def sync_age_yellow(self):
		return self.model_settings['sync_age_yellow']
	
	@property
	def api_rate_limit(self):
		return self.model_settings['api_rate_limit']
	
	@property
	def api_request_fields(self):
		# Start with the standard fields
		# Then extend them with the fields from model settings
		api_fields = settings.DEVICE_API_STANDARD_FIELDS
		api_fields.update(self.model_settings.get('standard_fields', {}))
		if self.wearable_allowed:
			api_fields['is_attached'] = True
		
		return api_fields
	
	
	#	Methods (remote URLs)
	
	
	#	Methods (authentication)
	def get_approval_request(self, request_key=None):
		if request_key:
			return self.approvals.filter(request_key=request_key).first()
		else:
			return self.approvals.all().first()
	
	def new_auth_key(self, approval_request=None):
		if approval_request:
			target_obj = approval_request
		else:
			target_obj = self
		
		new_key = uuid.uuid4()
		new_key_timestamp = timezone.now()
		new_key_hash = psv_hash256(new_key, self.authorization.init_secret, str(new_key_timestamp))
		
		target_obj.auth_key_hash = new_key_hash
		target_obj.timestamp_authkey = new_key_timestamp
		target_obj.save()
		
		return new_key
	
	def check_auth_key(self, input_key, approval_request=None):
		if approval_request:
			target_obj = approval_request
		else:
			target_obj = self
		
		input_hash = psv_hash256(input_key, self.authorization.init_secret, str(target_obj.timestamp_authkey))
		
		if input_hash == target_obj.auth_key_hash:
			return True
		else:
			return False
	
	def check_region(self, region_name):
		if self.attached:
			if self.region.name == region_name:
				return True
			else:
				return False
		else:
			return None
	
	#	Methods (universal)
	def get_owner(self):
		return_type = 'unknown'
		return_obj = None
		if self.group_owned:
			return_type = 'group'
			return_obj = self.group
		else:
			return_type = 'avatar'
			return_obj = self.owner_account
		
		return (return_type, return_obj)
	
	def get_model(self):
		return getattr(self, self.type, None)
	
	def set_timestamp_sync(self):
		if self.pk:
			return device.objects.filter(pk=self.pk).update(timestamp_sync=timezone.now())
		else:
			return False
	
	def __unicode__(self):
		return '%s (%s)' % (self.name, self.type)
	
	def save(self, *args, **kwargs):
		if not self.pk:
			self.app = self.__class__
			self.type = self.__class__.__name__
		super(device, self).save(*args, **kwargs)

#	Authentication used to initialize an API connection.
#	Equivalent to the application token/secret in an OAuth handshake.
class device_authorization_token(models.Model):
	parent = models.ForeignKey('device_authorization', on_delete=models.CASCADE, related_name='tokens')
	version = models.PositiveIntegerField(blank=False)
	
	init_key = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False)
	init_secret = models.TextField(blank=True, null=True, editable=False)
	is_active = models.BooleanField(default=True, blank=True, verbose_name='active')
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_expire = models.DateTimeField(blank=True, null=True, verbose_name='expiration date/time')
	
	@property
	def init_key_str(self):
		return str(self.init_key)
	
	@property
	def active(self):
		if self.is_active and self.init_secret and self.parent.active:
			# Token is valid
			if self.timestamp_expire:
				# Token expiration date exists
				if self.timestamp_expire > timezone.now():
					# Expiration date is in the future
					return True
				else:
					return False
			else:
				# Token has no expiration date
				return True
		else:
			# Token is marked inactive or has no init_secret
			return False
	
	@property
	def deprecated(self):
		if self.timestamp_expire:
			return True
		else:
			return False
	
	# Returns a tuple containing a pass/fail boolean and a reason for failure
	def validate(self, init_request, owner_key, object_key):
		status = False
		reason = ''
		
		if self.active:
			if init_request == psv_hash(owner_key, object_key, self.init_key_str, self.init_secret):
				if self.parent.check_avatar(owner_key):
					status = True
					reason = 'ok'
				else:
					status = False
					reason = 'user_invalid'
			else:
				status = False
				reason = 'init_request_invalid'
		else:
			status = False
			reason = 'authorization_revoked'
		
		return (status, reason)
	
	def save(self, *args, **kwargs):
		if not self.pk:
			self.init_secret = psv_hash256(self.init_key_str, str(self.timestamp_post))
		super(device_authorization_token, self).save(*args, **kwargs)
	
	class Meta:
		unique_together = (('parent', 'version'),)

class device_authorization(models.Model):
	name = models.CharField(max_length=64)
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	notes = models.TextField(blank=True, null=True)
	type = models.CharField(max_length=24, choices=device_type_choices(), blank=True, null=True)
	
	active = models.BooleanField(default=True, blank=True)
	allowed_users = models.ManyToManyField(avatar, blank=True)
	deprecation_days_override = models.PositiveIntegerField(blank=True, null=True)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	@property
	def available(self):
		if self.active:
			return self.tokens.filter(is_active=True).count()
		else:
			return False
	
	@property
	def deprecation_days(self):
		if self.deprecation_days_override:
			return self.deprecation_days_override
		else:
			return settings.DEVICE_AUTH_DEPRECATION_DAYS
	
	@property
	def current_token(self):
		return self.tokens.filter(is_active=True).filter(models.Q(timestamp_expire__isnull=True) or models.Q(timestamp_expire__lt=timezone.now())).order_by('-version').first()
	
	def check_avatar(self, user_key):
		# First, check the allowed_users list
		# As a fallback, check the owner's avatars
		# Also, if active is not True, always return False
		if not self.active:
			return False
		elif self.allowed_users.filter(key=user_key).exists():
			return True
		elif self.owner.grid_avatars.filter(key=user_key).exists():
			return True
		else:
			return False
	
	def new_token(self, replace=False):
		existing = self.tokens.all().order_by('-version')
		new_version = existing.count() + 1
		if replace and new_version > 1:
			expired_token = self.current_token
			if expired_token:
				expired_token.timestamp_expire = timezone.now() + timedelta(days=self.deprecation_days)
				expired_token.save()
		device_authorization_token.objects.create(parent=self, version=new_version)

#	Queue to track device initializations requiring manual approval.
#	This is a security mechanism that can be set for certain models subclassing device.
#	It is also required when an already-initialized device tries to re-initialize.
class device_approval_request(models.Model):
	REQUEST_TYPE_OPTIONS = (
		('new', 'New Device'),
		('reauth', 'Re-Authorization'),
	)
	
	device = models.ForeignKey(device, on_delete=models.CASCADE, related_name='approvals')
	approver_account = models.ForeignKey(User, null=True, editable=False, on_delete=models.SET_NULL, related_name='device_approval_requests')
	approver = models.ForeignKey(avatar, editable=False, on_delete=models.CASCADE, related_name='device_approval_requests')
	
	request_key = models.UUIDField(default=uuid.uuid4)
	request_type = models.CharField(max_length=24, choices=REQUEST_TYPE_OPTIONS)
	request_pin_hash = models.TextField(null=True, blank=True, editable=False)
	auth_key_hash = models.TextField(blank=True, null=True, editable=False)
	
	request_open = models.BooleanField(default=True, db_index=True)
	request_approved = models.BooleanField(default=False, editable=False, db_index=True)
	approver_notified = models.BooleanField(default=False, editable=False, db_index=True)
	
	approver_ip = models.GenericIPAddressField(blank=True, null=True, editable=False)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_expire = models.DateTimeField(blank=True, null=True, verbose_name='expiration date/time')
	timestamp_reviewed = models.DateTimeField(blank=True, null=True, verbose_name='date/time reviewed')
	timestamp_authkey = models.DateTimeField(blank=True, null=True, verbose_name='date/time auth key assigned')
	
	@property
	def request_key_str(self):
		return str(self.request_key)
	
	@property
	def anonymous(self):
		if self.approver_account:
			return False
		else:
			return True
	
	@property
	def request_reviewed(self):
		if self.timestamp_reviewed:
			return True
		else:
			return False
	
	@property
	def status(self):
		if self.request_open:
			if self.is_expired:
				return 'expired'
			elif self.request_reviewed:
				return 'open'
			elif self.approver_notified:
				return 'new'
			else:
				return 'ready'
		else:
			if self.request_reviewed and self.request_approved and self.approver_ip:
				return 'approved'
			elif self.request_reviewed:
				return 'denied'
			return 'closed'
	
	@property
	def expiration_date(self):
		if self.timestamp_expire:
			return self.timestamp_expire
		else:
			return timezone.now() + timedelta(hours=settings.DEVICE_APPROVAL_REQUEST_MAXAGE)
	
	@property
	def is_expired(self):
		if self.expiration_date > timezone.now():
			return False
		else:
			return True
	
	@property
	def is_approved(self):
		if self.status == 'approved':
			return True
		else:
			return False
	
	@property
	def is_open(self):
		if self.status == 'open' or self.status == 'new':
			return True
		else:
			return False
	
	# When invoking this function, make sure you capture the output!
	# The request PIN is not stored in plain text in the database.
	def get_request_pin(self, pin_required=False):
		if self.anonymous or pin_required:
			request_pin_source = rand_int_list(6)
			request_pin = ''.join(map(str, request_pin_source))
			self.request_pin_hash = psv_hash256(request_pin, self.approver.key_str)
			self.save()
			return request_pin
		else:
			# This validation method is only needed for anonymous requests
			return False
	
	def check_request_pin(self, pin_input, approver_key):
		if self.is_open and self.request_pin_hash:
			if psv_hash256(pin_input, approver_key) == self.request_pin_hash:
				return True
			else:
				return False
		else:
			# Always return false if this is not an open request, or if there's no hash to check
			return False
	
	# Extra URL handshake for anonymous approval links
	def check_request_url_key(self, url_key_input):
		if self.anonymous and self.is_open:
			if psv_hash(self.device.key_str, self.approver.key_str) == url_key_input:
				return True
			else:
				return False
		else:
			return False
	
	# Check whether this request can be accessed
	def can_access_request(self, request=False):
		if request:
			# To do!
			return False
		else:
			return False
	
	#def review_request(self, action, request):
	
	def save(self, *args, **kwargs):
		if self.is_expired and self.request_open:
			self.request_open = False
		
		if self.approver_notified and not self.timestamp_expire:
			self.timestamp_expire = self.expiration_date
		
		super(device_approval_request, self).save(*args, **kwargs)
	
	class Meta:
		ordering = ['-timestamp_post', ]









