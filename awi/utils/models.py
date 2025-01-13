#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for Django models
#	=================

from django.db import models
from django.utils import timezone

#	Since Django is stupidly picky about what it will accept for model field choices, 
#	I have to write a function that will turn the output of .keys() from a dict into tuple pairs.
def dict_key_choices(source_dict):
	keys = source_dict.keys()
	tuple_list = []
	
	for key in keys:
		tuple_list.append((key, key))
	
	return tuple_list

class TimestampModel(models.Model):
	"""Abstract base class for standard timestamps in models"""
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	class Meta:
		abstract = True
