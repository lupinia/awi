#	Election Map - Electoral Data Visualization (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import datetime
import math

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from awi.utils.models import TimestampModel

# Stupidest function ever
# This exact code directly in the default attribute throws an exception during makemigrations:
#	TypeError: can't compare datetime.datetime to datetime.time
# But if I move it to a function?  Works fine.
def default_closing_time():
	return datetime.time(hour=19, tzinfo=timezone.get_current_timezone())

@python_2_unicode_compatible
class state(models.Model):
	name = models.CharField(max_length=128)
	abbr = models.CharField(max_length=2, unique=True)
	split_presidential = models.BooleanField(default=False, blank=True)
	polls_close = models.TimeField(default=default_closing_time)
	
	house_seats = models.PositiveSmallIntegerField(blank=True)
	presidential_votes_override = models.PositiveSmallIntegerField(blank=True, default=0)
	senate1_class = models.PositiveSmallIntegerField(choices=settings.SENATE_CLASSES, default=0, blank=True)
	senate2_class = models.PositiveSmallIntegerField(choices=settings.SENATE_CLASSES, default=0, blank=True)
	
	@property
	def presidential_votes(self):
		if self.presidential_votes_override:
			return self.presidential_votes_override
		else:
			return self.house_seats + 2
	
	@property
	def polls_open(self):
		if timezone.now().time() > self.polls_close:
			return False
		else:
			return True
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']

@python_2_unicode_compatible
class election(TimestampModel):
	year = models.PositiveSmallIntegerField(unique=True, db_index=True)
	past = models.BooleanField(default=False, blank=True, db_index=True)
	day = models.DateField(blank=True)
	
	house_cycle = models.BooleanField(default=False, blank=True, db_index=True)
	presidential_cycle = models.BooleanField(default=False, blank=True, db_index=True)
	senate_class = models.PositiveSmallIntegerField(choices=settings.SENATE_CLASSES, default=0, blank=True, db_index=True)
	
	@property
	def senate_cycle(self):
		if self.senate_class > 0:
			return True
		else:
			return False
	
	def __str__(self):
		return unicode(self.year) # type: ignore
	
	def save(self, *args, **kwargs):
		if not self.day:
			new_day = datetime.date(year=self.year, month=11, day=2)
			while new_day.weekday() != 1:
				new_day = new_day.replace(day=new_day.day+1)
			self.day = new_day
			
		super(election, self).save(*args, **kwargs)

@python_2_unicode_compatible
class election_seats(TimestampModel):
	state = models.ForeignKey(state, on_delete=models.CASCADE, related_name='election_seats')
	election_year = models.ForeignKey(election, on_delete=models.CASCADE, related_name='state_config')
	
	house_seats = models.PositiveSmallIntegerField(blank=True)
	electoral_votes = models.PositiveSmallIntegerField(blank=True)
	senate_special = models.BooleanField(default=False, blank=True, db_index=True)
	
	last_party_president = models.CharField(max_length=1, choices=settings.ELECTION_PARTIES, null=True, blank=True)
	last_party_senate = models.CharField(max_length=1, choices=settings.ELECTION_PARTIES, null=True, blank=True)
	last_party_senate_special = models.CharField(max_length=1, choices=settings.ELECTION_PARTIES, null=True, blank=True)
	last_party_house_data = JSONField(null=True, blank=True)
	
	def __str__(self):
		return '%s - %d' % (self.state.abbr, self.election_year.year)
	
	class Meta:
		unique_together = (('state', 'election_year'),)
		ordering = ['-election_year','state']

@python_2_unicode_compatible
class data_source(TimestampModel):
	name = models.CharField(max_length=128)
	slug = models.SlugField(max_length=64, unique=True, db_index=True)
	url = models.URLField(max_length=1024, null=True, blank=True)
	notes = models.TextField(null=True, blank=True)
	projected = models.BooleanField(default=False, blank=True, db_index=True)
	certified = models.BooleanField(default=False, blank=True, db_index=True)
	owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='election_data_sources')
	
	def __str__(self):
		return self.name

class results(TimestampModel):
	state = models.ForeignKey(state, on_delete=models.CASCADE, related_name='%(class)s')
	election_year = models.ForeignKey(election, on_delete=models.CASCADE, related_name='%(class)s')
	party = models.CharField(max_length=1, choices=settings.ELECTION_PARTIES, default='I')
	source = models.ForeignKey(data_source, on_delete=models.CASCADE, related_name='%(class)s')
	source_note = models.CharField(max_length=128, null=True, blank=True)
	
	projected = models.BooleanField(default=False, blank=True, db_index=True)
	certified = models.BooleanField(default=False, blank=True, db_index=True)
	flipped = models.BooleanField(default=False, blank=True, db_index=True)
	
	@property
	def is_projected(self):
		if self.certified:
			return False
		else:
			return self.projected
	
	@property
	def status(self):
		if self.certified:
			return 'certified'
		elif self.is_projected:
			return 'projected'
		else:
			return ''
	
	@property
	def name(self):
		return self.state.abbr
	
	def append_status_label(self, input):
		if self.status:
			return '%s (%s)' % (input, self.status.capitalize())
		else:
			return input
		
	class Meta:
		abstract = True
		ordering = ['state', '-certified', 'projected']

@python_2_unicode_compatible
class results_house(results):
	district = models.PositiveSmallIntegerField(default=1)
	
	@property
	def name(self):
		return '%s-%d' % (self.state.abbr, self.district)
	
	def __str__(self):
		return '%s: %s' % (self.name, self.append_status_label(self.party))
	
	class Meta(results.Meta):
		unique_together = (('state', 'election_year', 'source', 'district'),)
		ordering = ['state', 'district', '-certified', 'projected']

@python_2_unicode_compatible
class results_senate(results):
	senate_class = models.PositiveSmallIntegerField(choices=settings.SENATE_CLASSES, default=0, blank=True, db_index=True)
	
	def __str__(self):
		return '%s: %s' % (self.state.abbr, self.append_status_label(self.party))
	
	class Meta(results.Meta):
		unique_together = (('state', 'election_year', 'source', 'senate_class'),)

@python_2_unicode_compatible
class results_president(results):
	electoral_votes = models.PositiveSmallIntegerField(default=1)
	district = models.PositiveSmallIntegerField(default=0)
	
	@property
	def district_name(self):
		return '%s-%d' % (self.state.abbr, self.district)
	
	@property
	def name(self):
		if self.district:
			return self.district_name
		else:
			return self.state.abbr
	
	def __str__(self):
		return '%s: %s' % (self.district_name, self.append_status_label(self.party))
	
	class Meta(results.Meta):
		unique_together = (('state', 'election_year', 'source', 'district'),)
