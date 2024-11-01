#	Election Map - Electoral Data Visualization (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import math

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class state(models.Model):
	name = models.CharField(max_length=128)
	abbr = models.CharField(max_length=2, unique=True)
	split_presidential = models.BooleanField(default=False, blank=True)
	
	
	def __unicode__(self):
		return self.name

class election(models.Model):
	year = models.PositiveSmallIntegerField(unique=True)
	past = models.BooleanField(default=False, blank=True, db_index=True)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def __unicode__(self):
		return unicode(self.year)

class election_seats(models.Model):
	state = models.ForeignKey(state, on_delete=models.CASCADE, related_name='election_seats')
	election_year = models.ForeignKey(election, on_delete=models.CASCADE, related_name='election_seats')
	house_seats = models.PositiveSmallIntegerField()
	electoral_votes = models.PositiveSmallIntegerField()
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def __unicode__(self):
		return '%s - %s' % (self.state.abbr, unicode(self.election_year))

class data_source(models.Model):
	name = models.CharField(max_length=128)
	slug = models.SlugField(max_length=64, unique=True, db_index=True)
	url = models.URLField(max_length=1024, null=True, blank=True)
	notes = models.TextField(null=True, blank=True)
	projected = models.BooleanField(default=False, blank=True, db_index=True)
	certified = models.BooleanField(default=False, blank=True, db_index=True)
	owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='election_data_sources')
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def __unicode__(self):
		return self.name

class results(models.Model):
	state = models.ForeignKey(state, on_delete=models.CASCADE, related_name='%(class)s')
	election_year = models.ForeignKey(election, on_delete=models.CASCADE, related_name='%(class)s')
	party = models.CharField(max_length=1, choices=settings.ELECTION_PARTIES, default='I')
	source = models.ForeignKey(data_source, on_delete=models.CASCADE, related_name='%(class)s')
	source_note = models.CharField(max_length=128, null=True, blank=True)
	
	projected = models.BooleanField(default=False, blank=True, db_index=True)
	certified = models.BooleanField(default=False, blank=True, db_index=True)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	@property
	def is_projected(self):
		if certified:
			return False
		else:
			return self.is_projected
	
	class Meta:
		abstract = True

class results_house(results):
	district = models.PositiveSmallIntegerField(default=1)
	
	def __unicode__(self):
		return '%s-%d' % (self.state.abbr, self.district)

class results_senate(results):
	def __unicode__(self):
		return '%s-%d' % (self.state.abbr, self.district)

class results_president(results):
	electoral_votes = models.PositiveSmallIntegerField(default=1)
	
	def __unicode__(self):
		return '%s-%d' % (self.state.abbr, self.district)
