#	DeerAttend (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import uuid

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe

from awi.utils.models import TimestampModel
from awi.utils.text import summarize

@python_2_unicode_compatible
class venue(TimestampModel):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	
	# Location
	address = models.CharField(max_length=250, verbose_name='street address')
	city = models.CharField(max_length=250)
	state = models.CharField(max_length=250, blank=True, null=True, verbose_name='state/province/territory')
	country = models.CharField(max_length=250)
	geo_lat = models.DecimalField(decimal_places=15, max_digits=20, blank=True, null=True, db_index=True, verbose_name='latitude', help_text='Positive numbers are northern hemisphere, negative numbers are southern.')
	geo_long = models.DecimalField(decimal_places=15, max_digits=20, blank=True, null=True, db_index=True, verbose_name='longitude', help_text='Positive numbers are eastern hemisphere, negative numbers are western.')
	
	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerattend:filter_venue', kwargs={'slug':self.slug,})
	
	def get_city(self):
		if self.state:
			return "%s, %s, %s" % (self.city, self.state, self.country)
		else:
			return "%s, %s" % (self.city, self.country)

@python_2_unicode_compatible
class attendance_flag(TimestampModel):
	name = models.CharField(max_length=250)
	slug = models.SlugField(unique=True)
	img_width = models.IntegerField(null=True, blank=True)
	img_height = models.IntegerField(null=True, blank=True)
	icon = models.ImageField(upload_to='attend_icons', height_field='img_height', width_field='img_width')
	
	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerattend:filter_flag', kwargs={'slug':self.slug,})
	
	def get_icon_url(self):
		return "%s%s" % (settings.MEDIA_URL, self.icon.name)
	
	class Meta:
		verbose_name = 'flag'

@python_2_unicode_compatible
class event_type(TimestampModel):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	notes = models.TextField(null=True, blank=True)
	map_color = models.CharField(max_length=6, blank=True, default='4a3bd0', help_text="Hexadecimal-format color code for events of this type in the map view.")
	
	# Annoyingly, Mapbox appears to have no way to actually USE the newest Maki icons in a map, so this field is a bit pointless at the moment.  But, hopefully someday it can be used to create more interesting markers.
	symbol = models.CharField(max_length=40, blank=True, null=True, verbose_name='Maki icon', help_text=mark_safe('Icon to use from the <a href="https://www.mapbox.com/maki-icons/">Mapbox Maki</a> set.  Leave blank to use the number of items of this type as the symbol.'))
	
	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerattend:filter_type', kwargs={'slug':self.slug,})
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.notes, length=length, prefer_long=True)
		else:
			return summarize(body=self.notes, length=length)
	
	@property
	def summary_short(self):
		return self.get_summary()
	
	@property
	def summary_long(self):
		return self.get_summary(512)
	
	class Meta:
		verbose_name = 'type'

@python_2_unicode_compatible
class event(TimestampModel):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	notes = models.TextField(null=True, blank=True)
	type = models.ForeignKey(event_type, on_delete=models.PROTECT)
	mature = models.BooleanField(help_text='Check this box to indicate a mature/18+ event.', db_index=True)
	
	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerattend:filter_event', kwargs={'slug':self.slug,})
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.notes, length=length, prefer_long=True)
		else:
			return summarize(body=self.notes, length=length)
	
	@property
	def summary_short(self):
		return self.get_summary()
	
	@property
	def summary_long(self):
		return self.get_summary(512)

@python_2_unicode_compatible
class event_instance(TimestampModel):
	event = models.ForeignKey(event, on_delete=models.PROTECT)
	instance = models.CharField(max_length=15, verbose_name='instance label', help_text="Label for the specific instance of an event.  Ideally a year, but not necessarily.  For example, 'Jan 2012', or '3'.")
	name = models.CharField(max_length=100, null=True, blank=True, help_text="Override the standard format of 'event_instance.event.name event_instance.instance'")
	slug = models.SlugField(unique=True)
	uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	
	# Attendance Details
	confirmed = models.BooleanField(default=True, db_index=True, help_text='Check this box if attendance at this event has been confirmed (purchased registration, etc).')
	flags = models.ManyToManyField(attendance_flag,blank=True)
	notes = models.TextField(null=True, blank=True)
	photos = models.ForeignKey('deertrees.category', null=True, blank=True, on_delete=models.SET_NULL, help_text='Select a Category that contains photos taken at this event.')
	report = models.ForeignKey('deerbooks.page', null=True, blank=True, on_delete=models.SET_NULL, help_text='Select a Page describing/related to experiences at this event.')
	
	# Time and Place
	date_start = models.DateField(null=True, blank=True, db_index=True, verbose_name='start date')
	date_end = models.DateField(null=True, blank=True, db_index=True, verbose_name='end_date')
	venue = models.ForeignKey(venue, related_name='events', on_delete=models.PROTECT)
	
	def get_name(self):
		if self.name:
			return self.name
		else:
			return "%s %s" % (self.event, self.instance)
	
	@property
	def is_tentative(self):
		# Check whether this is an upcoming but unconfirmed appearance.
		if self.date_start > timezone.now().date() and not self.confirmed:
			return True
		else:
			return False
	
	@property
	def is_upcoming(self):
		# Check whether this is an upcoming confirmed appearance.
		if self.date_start > timezone.now().date() and self.confirmed:
			return True
		else:
			return False
	
	def __str__(self):
		return self.get_name()
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.notes, length=length, prefer_long=True)
		else:
			return summarize(body=self.notes, length=length)
	
	@property
	def summary_short(self):
		return self.get_summary()
	
	@property
	def summary_long(self):
		return self.get_summary(512)
	
	# Special case:  For search indexing, we want to check the parent event for notes if this object doesn't have anything.
	# The extra database hit is worth it for more-relevant search results.
	@property
	def summary_search(self):
		if not self.notes and self.event.notes:
			fallback = self.event.get_summary(255)
		else:
			fallback = None
		
		return summarize(body=self.notes, length=255, fallback=fallback)
	
	class Meta:
		verbose_name = 'event instance'
