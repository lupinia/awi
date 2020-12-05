#	User Account Tools (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe

class name_history(models.Model):
	profile = models.ForeignKey('person', related_name='past_names')
	
	grid_name_first = models.CharField(max_length=50)
	grid_name_last = models.CharField(max_length=50)
	grid_username = models.CharField(max_length=100)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	@property
	def grid_name(self):
		return '%s %s' % (self.grid_name_first, self.grid_name_last)
	
	def __unicode__(self):
		return '%s (Profile: %d)' % (self.grid_name, self.pk)

class person(models.Model):
	account = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='profiles')
	display_name = models.CharField(max_length=250)
	
	grid = models.CharField(max_length=100, choices=settings.GRID_OPTIONS, help_text='Select the virtual world/"grid" for this user.')
	key = models.UUIDField(db_index=True, help_text=mark_safe('The unique identifier for this user.  <a href="http://wiki.secondlife.com/wiki/Category:LSL_Key" target="_BLANK">More info</a>.'))
	
	grid_name_first = models.CharField(max_length=50, blank=True, editable=False)
	grid_name_last = models.CharField(max_length=50, blank=True, editable=False)
	grid_username = models.CharField(max_length=100) #TODO: Validator!
	grid_username_cur = models.CharField(max_length=100, editable=False)
	
	is_bot = models.BooleanField(default=False, blank=True)
	
	date_gridcreate = models.DateField(blank=True, null=True)
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_namechange = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='date/time of last name change')
	
	@property
	def grid_name(self):
		return '%s %s' % (self.grid_name_first, self.grid_name_last)
	
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
				name_history.objects.create(profile=self, grid_username=self.grid_username_cur, grid_name_first=self.grid_name_first, grid_name_last=self.grid_name_last)
				self.grid_name_first, self.grid_name_last, self.grid_username = self.normalize_names()
				self.grid_username_cur = self.grid_username
				self.timestamp_namechange = timezone.now()
		
		else:
			# This is a new entry, gotta do some cleanup
			self.grid_name_first, self.grid_name_last, self.grid_username = self.normalize_names()
			self.grid_username_cur = self.grid_username
		
		super(person, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return '%s (%s)' % (self.grid_name, self.get_grid_display())
	
	class Meta:
		unique_together = (('key', 'grid'),)
