#	DeerAttend (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import uuid

from django.db import models
from django.utils import timezone

from deertrees.models import category
from deerbooks.models import page

class venue(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	timestamp_mod = models.DateTimeField(auto_now=True)
	timestamp_post = models.DateTimeField(default=timezone.now)
	
	# Location
	address = models.CharField(max_length=250)
	city = models.CharField(max_length=250)
	state = models.CharField(max_length=250, blank=True, null=True)
	country = models.CharField(max_length=250)
	geo_lat = models.DecimalField(decimal_places = 15, max_digits = 20, blank=True, null=True)
	geo_long = models.DecimalField(decimal_places = 15, max_digits = 20, blank=True, null=True)
	
	def __unicode__(self):
		return self.name
	
	def get_city(self):
		if self.state:
			return "%s, %s, %s" % (self.city, self.state, self.country)
		else:
			return "%s, %s" % (self.city, self.country)

class attendance_flag(models.Model):
	name = models.CharField(max_length=250)
	slug = models.SlugField(unique=True)
	img_width = models.IntegerField(null=True,blank=True)
	img_height = models.IntegerField(null=True,blank=True)
	icon = models.ImageField(upload_to='attend_icons',height_field='img_height',width_field='img_width')
	
	def __unicode__(self):
		return self.name

class event_type(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	notes = models.TextField(null=True, blank=True)
	
	def __unicode__(self):
		return self.name

class event(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	notes = models.TextField(null=True, blank=True)
	type = models.ForeignKey(event_type)
	timestamp_mod = models.DateTimeField(auto_now=True)
	timestamp_post = models.DateTimeField(default=timezone.now)
	mature = models.BooleanField()
	
	def __unicode__(self):
		return self.name

class event_instance(models.Model):
	event = models.ForeignKey(event)
	instance = models.CharField(max_length=15, help_text="Label for the specific instance of an event.  Ideally a year, but not necessarily.  For example, 'Jan 2012', or '3'.")
	name = models.CharField(max_length=100, null=True, blank=True, help_text="Override the standard format of 'event_instance.event.name event_instance.instance'")
	slug = models.SlugField(unique=True)
	timestamp_mod = models.DateTimeField(auto_now=True)
	timestamp_post = models.DateTimeField(default=timezone.now)
	uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	
	# Attendance Details
	confirmed = models.BooleanField(default=True)
	flags = models.ManyToManyField(attendance_flag,blank=True)
	notes = models.TextField(null=True, blank=True)
	photos = models.ForeignKey(category, null=True, blank=True)
	report = models.ForeignKey(page, null=True, blank=True)
	
	# Time and Place
	date_start = models.DateField(null=True, blank=True)
	date_end = models.DateField(null=True, blank=True)
	venue = models.ForeignKey(venue)
	
	def get_name(self):
		if self.name:
			return self.name
		else:
			return "%s %s" % (self.event, self.instance)
	
	def is_tentative(self):
		# Check whether this is an upcoming but unconfirmed appearance.
		if self.date_start > timezone.now().date() and not self.confirmed:
			return True
	
	def is_upcoming(self):
		# Check whether this is an upcoming confirmed appearance.
		if self.date_start > timezone.now().date() and self.confirmed:
			return True
	
	def __unicode__(self):
		return self.get_name()
