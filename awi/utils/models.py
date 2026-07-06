#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for Django models
#	=================

from django.db import models
from django.utils import timezone

def dict_key_choices(source_dict):
	"""
	dict_key_choices(dict) -> [(key, key),]
	Takes any dictionary, and returns its keys as a list of tuple pairs
	This is necessary to format the keys of a dictionary for use as model field choices
	"""
	keys = source_dict.keys()
	tuple_list = []
	
	for key in keys:
		tuple_list.append((key, key))
	
	return tuple_list

# Abstract model base classes
class TimestampModel(models.Model):
	"""
	Abstract base class for standard timestamps in models
	Includes the following fields: 
		timestamp_mod:  Auto-updated with every call to model.save()
		timestamp_create:  Defaults to timezone.now() on creation, non-editable
		timestamp_post:  Defaults to timezone.now() on creation, editable
	"""
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_create = models.DateTimeField(default=timezone.now, db_index=True, editable=False, verbose_name='date/time created')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time published')
	
	class Meta:
		abstract = True
		get_latest_by = 'timestamp_post'
