#	DeerLand - Virtual World Property Management (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.conf import settings
from django.db import models
from django.utils import timezone

class estate(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	grid = models.CharField(max_length=100, choices=settings.GRID_OPTIONS, help_text='Select the virtual world/"grid" for this estate and its regions.')
	owner = models.ForeignKey('usertools.person', on_delete=models.SET_NULL, null=True, blank=True)

class region(models.Model):
	RATING_OPTIONS = (
		('PG', 'General'),
		('MATURE', 'Moderate'),
		('ADULT', 'Adult'),
		('UNKNOWN', 'Unknown'),
	)
	
	name = models.CharField(max_length=64)
	estate = models.ForeignKey(estate, on_delete=models.PROTECT)
	
	rating = models.CharField(max_length=10, choices=RATING_OPTIONS, default='UNKNOWN')
	data_pos_x = models.IntegerField(null=True, blank=True)
	data_pos_y = models.IntegerField(null=True, blank=True)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	timestamp_check = models.DateTimeField(blank=True, null=True, verbose_name='date/time of last data check')
