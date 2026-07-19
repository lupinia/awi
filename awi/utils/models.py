#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for Django models
#	=================

from django.db import models
from django.utils import timezone

from awi.utils import types as typeutils

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

def params_to_Q(params):
	"""
	params_to_Q(dict) -> (models.Q(key=value) & ...)
	
	Turns a dictionary of query parameters into a chain of AND-joined Q objects
	Useful when parameters usually defined as a dictionary need to be appended to another query
	"""
	chain = None
	for k, v in params.iteritems():
		if chain is None:
			# First iteration
			chain = models.Q(**{k:v,})
		else:
			# Subsequent iterations
			chain = chain & models.Q(**{k:v,})
	
	return chain


# Abstract model base classes and mixin classes
class ChoicesMixin():
	"""
	Special model mixin for working with field choices.
	Provides convenience methods for splitting any attributes that define 
	field choices in the standard Django format (list of tuple pairs, values then labels). 
	Adds the following additional attributes: 
		attrname_SPLIT:  If attrname is iterable, returns two lists: values, and labels 
		attrname_VALUES:  If attrname is iterable, returns only the values list 
		attrname_LABELS:  If attrname is iterable, returns only the labels list 
	"""
	def _choices_attr_is_iter(self, name):
		"""Check whether the specified attribute defines choices (an iterable of tuple pairs)"""
		return typeutils.is_iterable(getattr(self, name, None))
	
	def _choices_attr_has_labels(self, name):
		"""
		Check whether the specified attribute defines choices with labels 
		(an iterable of tuple pairs)
		Returns None if specified attribute is not iterable
		"""
		if self._choices_attr_is_iter(name):
			# The underlying attribute exists and is an iterable
			# Let's see if it's the right kind of iterable
			testattr = getattr(self, name, [None])
			if typeutils.is_iterable(testattr[0]) and len(testattr[0]) > 1:
				# First element of this list is also iterable and contains more than one element
				return True
			else:
				return False
		
		else:
			# Specified attribute does not exist or is not iterable
			return None
	
	def _choices_attr_split(self, name):
		"""
		Split the specified attribute into two lists, values and labels
		If attribute has no labels, second return value will be None
		If attribute is not iterable, both values will be None
		"""
		attrcheck = self._choices_attr_has_labels(name)
		if attrcheck is None:
			# Specified attribute is not iterable
			# Not sure how you even managed this
			return (None, None)
		
		elif attrcheck:
			# Specified attribute is an iterable and appears to have labels
			return zip(*getattr(self, name, None))
		
		else:
			# Specified attribute is iterable, but does not have labels
			return (getattr(self, name, None), None)
	
	def _choices_attr_values(self, name):
		"""Retrieve only the values of the specified attribute, stripped of labels"""
		values, labels = self._choices_attr_split(name)
		return values
	
	def _choices_attr_labels(self, name):
		"""Retrieve only the labels of the specified attribute, if any exist"""
		values, labels = self._choices_attr_split(name)
		return labels
	
	# System method override
	def __getattr__(self, name):
		if name.endswith(('_SPLIT', '_VALUES', '_LABELS')):
			# We're specifically trying to use this mixin, so let's check it
			attrname, action = name.rsplit('_', 1)
			if self._choices_attr_is_iter(attrname):
				# The underlying attribute exists and is an iterable
				# Whether it's the right *kind* of iterable is a "you" problem
				if action == 'VALUES':
					return self._choices_attr_values(attrname)
				elif action == 'SPLIT':
					return self._choices_attr_split(attrname)
				elif action == 'LABELS':
					return self._choices_attr_labels(attrname)
			
			else:
				# Not an iterable, so not sure what you're doing here
				raise AttributeError('%s is not formatted as a field choices attribute' % attrname)
		
		# Nothing to do here, so pass the request down the chain
		return super(ChoicesMixin, self).__getattr__(name)

class TimestampModel(models.Model):
	"""
	Abstract base class for standard timestamps in models
	Includes the following fields: 
		timestamp_mod:  Auto-updated with every call to model.save()
		timestamp_create:  Defaults to timezone.now() on creation, non-editable
		timestamp_post:  Defaults to timezone.now() on creation, editable
		timedisp:  Selects which timestamp is considered the "default".  Override TIMEDISP_OPTIONS_EXTRA to add more
	
	Static attributes for model settings in classes that inherit TimestampModel:
		TIMESTAMP_DEFAULT:  Set the default value of timedisp
		TIMEDISP_OPTIONS:  Add more timestamps and change priority order
			(Be careful not to delete the existing entries!)
	"""
	# Field choices constants
	TIMEDISP_OPTIONS = (
		('post', 'Published'),
		('create', 'Created'),
		('mod', 'Modified'),
	)
	
	# Other constants
	TIMESTAMP_DEFAULT = 'post'
	
	# Timestamp fields
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_create = models.DateTimeField(default=timezone.now, db_index=True, editable=False, verbose_name='date/time created')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time published')
	
	# System fields
	timedisp = models.CharField(max_length=10, choices=TIMEDISP_OPTIONS, default=TIMESTAMP_DEFAULT, verbose_name='primary timestamp', help_text='Determines which timestamp will be displayed as the primary timestamp in situations where only one is shown.')
	
	# Calculated properties and states
	@property
	def is_future(self):
		"""Boolean indicating whether this object has a publication date in the future"""
		if self.timestamp_post > timezone.now():
			return True
		else:
			return False
	
	
	class Meta:
		abstract = True
		get_latest_by = 'timestamp_post'
