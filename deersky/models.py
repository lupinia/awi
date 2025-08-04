#	DeerSky - Digital Almanac and Weather Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import math
import pytz

from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property

from awi.utils.models import TimestampModel

@python_2_unicode_compatible
class city(TimestampModel):
	label = models.CharField(max_length=128)
	country = models.CharField(max_length=3)
	lat = models.FloatField(blank=True, null=True)
	long = models.FloatField(blank=True, null=True)
	fictional = models.BooleanField(default=False, blank=True, help_text="Check this box if this city does not exist in real life (useful for roleplay/story settings).")
	
	timezone = models.CharField(max_length=250, default="UTC", db_index=True)
	timezone_order = models.DecimalField(max_digits=4, decimal_places=2, default=0, blank=True, db_index=True, help_text="Enter the standard (non-DST) UTC offset.  This will be used to sort the clocks (ascending, west to east).  Add -0.01 or 0.01 for timezones that do not observe DST.")
	primary_for_timezone = models.BooleanField(default=False, blank=True, help_text="Check this box to use this city as the default label when adding this timezone to a homepage.")
	
	enable_suntime = models.BooleanField(default=True, blank=True, verbose_name='enable sunrise/sunset time?')
	enable_moon = models.BooleanField(default=True, blank=True, verbose_name='enable moon phases?')
	
	def __str__(self):
		return self.label
	
	def now(self):
		return datetime.now(pytz.timezone(self.timezone))
	
	# Feels silly to do both, but .now() is always a method, so I'll be consistent
	@property
	def current_time(self):
		return self.now()
	
	# Can't calculate day/night, sunrise/sunset, or moon phases without coordinates
	@property
	def has_coords(self):
		if self.lat and self.long:
			return True
		else:
			return False
	
	@property
	def use_sun(self):
		if self.enable_suntime and self.has_coords:
			return True
		else:
			return False
	
	@property
	def use_moon(self):
		if self.enable_suntime and self.has_coords:
			return True
		else:
			return False
	
	@property
	def is_night(self):
		if self.use_sun:
			# Placeholder for using sunrise/sunset calculation
			# Not yet implemented
			return False
		
		else:
			# If we're not doing sunrise/sunset calculation, nothing to do here
			return False
	
	class Meta:
		unique_together = (('label', 'timezone'),)
		ordering = ['timezone_order', 'long']

@python_2_unicode_compatible
class homepage(TimestampModel):
	title = models.CharField(max_length=250, default="New Tab - Lupinia Studios")
	slug = models.SlugField(max_length=64, unique=True)
	owner = models.ForeignKey('auth.User', on_delete=models.PROTECT)
	public = models.BooleanField(default=False, blank=True, db_index=True, help_text="Check this box to show this homepage in a public list of available options.  When unchecked, it will still be available to anyone with the URL.")
	
	main_city = models.ForeignKey(city, on_delete=models.PROTECT, related_name='primary_for', verbose_name='city')
	backgrounds_override = models.ManyToManyField('sunset.background_tag', blank=True, help_text='Select specific background tags to override the default.  This will also override seasonal backgrounds.')
	default_backgrounds = models.BooleanField(default=True, blank=True, verbose_name='include default background tags?', help_text='If checked, the backgrounds override list will be used in addition to the default backgrounds, instead of replacing them.')
	
	# Widget:  Timer 
	enable_timer = models.BooleanField(default=True, blank=True, verbose_name='enable timer?')
	timer_default = models.PositiveSmallIntegerField(default=300, verbose_name='timer start time', help_text='Set the default start time for the timer widget (in seconds).')
	
	# Widget:  Secondary clocks
	enable_extraclocks = models.BooleanField(default=True, blank=True, verbose_name='enable secondary clocks?')
	
	def __str__(self):
		return self.title
	
	@property
	def cache_prefix(self):
		return 'deersky_homepage_%s' % self.slug
	
	@cached_property
	def city(self):
		# First try: Look it up by primary key
		main_city_obj = cache.get('deersky_city_%d' % self.main_city_id)
		if main_city_obj is None:
			# Second try: Get it from the database, and hope we never have to do this again
			main_city_obj = self.main_city
			cache.set('deersky_city_%d' % main_city_obj.pk, main_city_obj)
		
		return main_city_obj
	
	# Number of seconds until the next minute
	# Used to synchronize Javascript clock update code to server time
	def clock_sync(self):
		return (60 - self.city.now().second) * 1000
	
	@property
	def secondary_clocks(self):
		if not self.enable_extraclocks:
			# Nothing to do here
			# Task failed successfully
			return None
		
		else:
			clocklist = cache.get('%s_extraclocks' % self.cache_prefix)
			
			if clocklist is None:
				build_status = self.build_clocks()
				if build_status:
					return cache.get('%s_extraclocks' % self.cache_prefix)
				else:
					return None
			else:
				return clocklist
	
	# Rebuild and recache clocks
	def build_clocks(self):
		if not self.enable_extraclocks:
			# Nothing to do here
			# Task failed successfully
			return True
		
		# The original new tab page clock list only stored label and timezone
		# To support things like sunrise/sunset, we need the whole city object
		# This basically caches the city twice, but avoiding doing that is complicated 
		clockobjects = self.secondary_clock_set.all().select_related()
		if clockobjects:
			clocklist = []
			for clock in clockobjects:
				clocklist.append({
					'priority':clock.priority,
					'city':clock.city,
				})
			
			cache.set('%s_extraclocks' % self.cache_prefix, clocklist)
			return True
		
		else:
			return False

@python_2_unicode_compatible
class secondary_clock(models.Model):
	parent = models.ForeignKey(homepage, on_delete=models.CASCADE)
	city = models.ForeignKey(city, on_delete=models.CASCADE, related_name='secondary_for')
	priority = models.PositiveSmallIntegerField()
	
	def __str__(self):
		return self.city.label
	
	class Meta:
		unique_together = (('parent', 'city'), ('parent', 'priority'))
		ordering = ['city__timezone_order', 'city__long']
