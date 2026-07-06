#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for working with x.509 certificates
#	=================

import json
from datetime import datetime, timedelta
from dateutil import parser as dateparser

from django.conf import settings
from django.utils import timezone

from awi.utils import types as typeutils

# Object Definitions
class DN(object):
	"""Standard object representing the subject or issuer of a certificate"""
	cname = None
	name_first = None
	name_last = None
	initials = None
	email = None
	
	title = None
	org = None
	orgunit = None
	
	street = None
	city = None
	state = None
	country = None
	extra_fields = {}
	
	required_fields = [
		'email',
		'org',
		'country',
	]
	
	# Standard key : object attribute
	fieldmap = {
		'CN': 'cname',
		'emailAddress': 'email',
		'O': 'org',
		'OU': 'orgunit',
		'L': 'city',
		'ST': 'state',
		'C': 'country',
		'street': 'street',
		'title': 'title',
		'GN': 'name_first',
		'SN': 'name_last',
		'initials': 'initials',
	}
	
	def __init__(self, *args, **kwargs):
		if len(args) > 1:
			raise TypeError('only one positional argument accepted')
		elif args:
			# If we're here, we're typecasting, so this could be anything
			if isinstance(args[0], DN):
				other = args.pop(0)
				raw_input = other.as_dict()
				raw_input.update(kwargs)
				kwargs = self.set_kwargs(**raw_input)
			
			elif isinstance(args[0], dict):
				# Should be a formality to just unpack this
				raw_input = args.pop(0)
				raw_input.update(kwargs)
				kwargs = self.set_kwargs(**raw_input)
			
			elif typeutils.is_string(args[0]):
				raw_input = args.pop(0)
				if raw_input.startswith('{') and raw_input.endswith('}'):
					# If this raises an exception, we should pass it along, so no try/except block
					self = type(self).from_json(raw_input, **kwargs)
				elif '/' in raw_input:
					self = type(self).from_cli(raw_input, **kwargs)
				elif ',' in raw_input:
					self = type(self).from_http(raw_input, **kwargs)
				else:
					raise ValueError('unknown input string format')
			
			elif args[0] is None:
				# Initialize an empty object
				args = []
			
			else:
				raise TypeError('unable to convert %s to x509.DN object' % type(args[0]))
		
		if kwargs:
			kwargs = self.set_kwargs(**kwargs)
		
		super(DN, self).__init__(*args, **kwargs)
	
	def set_kwargs(self, **kwargs):
		if isinstance(kwargs.get('extra_fields', None), dict):
			self.extra_fields = kwargs.pop('extra_fields', {})
		
		attrs = kwargs.keys()
		for attr in attrs:
			if hasattr(self, attr):
				setattr(self, attr, kwargs.pop(attr, None))
			elif attr in self.fieldmap.keys():
				setattr(self, self.fieldmap[attr], kwargs.pop(attr, None))
			else:
				self.extra_fields[attr] = kwargs.pop(attr, None)
		
		return kwargs
	
	# Additional Properties
	@property
	def name(self):
		if self.cname:
			return self.cname
		elif self.name_first and self.name_last:
			return '%s %s' % (self.name_first, self.name_last)
		elif self.name_first:
			return self.name_first
		elif self.name_last:
			return self.name_last
		elif self.initials:
			return self.initials
		else:
			return None
	
	@property
	def display_location(self):
		parts = []
		if self.city:
			parts.append(self.city)
		if self.state:
			parts.append(self.state)
		if self.country:
			parts.append(self.country)
		
		if parts:
			return ', '.join(parts)
		else:
			return ''
	
	@property
	def display_label(self):
		if self.name:
			return self.name
		elif self.email:
			return self.email
		elif self.orgunit:
			if self.org:
				return '%s - %s' % (self.org, self.orgunit)
			else:
				return self.orgunit
		elif self.org:
			return self.org
		else:
			return ''
	
	
	# Validation
	@property
	def is_valid(self):
		return all(getattr(self, attr, None) for attr in self.required_fields)
	
	
	# Parsing and input
	@classmethod
	def from_json(cls, input_str, **kwargs):
		"""Deserialize from a JSON string"""
		parts = json.loads(input_str)
		parts.update(kwargs)
		return cls(**parts)
	
	@classmethod
	def from_http(cls, rawDN, **kwargs):
		"""Turn the standard string representation of a certificate DN into separate fields"""
		return cls.parse(rawDN, field_separator=',', **kwargs)
	
	@classmethod
	def from_cli(cls, rawDN, **kwargs):
		"""Turn the standard string representation of a certificate DN into separate fields"""
		if rawDN.endswith("\n"):
			rawDN = rawDN.replace("\n", '')
		if rawDN.startswith("subject= /"):
			rawDN = rawDN.replace("subject= /", '')
		if rawDN.startswith("issuer= /"):
			rawDN = rawDN.replace("issuer= /", '')
		
		return cls.parse(rawDN, field_separator='/', **kwargs)
	
	@classmethod
	def parse(cls, rawDN, field_separator=',', value_separator='=', **kwargs):
		"""
		Parse the single-line representation of a certificate subject into individual fields
		If successful, returns a dict of key-value pairs found in the string
		"""
		parts = {}
		lines = []
		
		if not typeutils.is_string(rawDN):
			raise TypeError('DN must be string')
		if not value_separator in rawDN:
			raise ValueError('value_separator (%s) not found in input string' % value_separator)
		if not field_separator in rawDN:
			raise ValueError('field_separator (%s) not found in input string' % field_separator)
		
		lines = rawDN.split(field_separator)
		for line in lines:
			if value_separator in line:
				tag, value = line.split(value_separator, 1)
				parts[tag] = value
		
		parts.update(kwargs)
		return cls(**parts)
	
	
	# Output
	def as_dict(self, rfc_fieldnames=False):
		parts = {}
		for k, attr in self.fieldmap.iteritems():
			a = getattr(self, attr, None)
			if a:
				if rfc_fieldnames:
					parts[k] = a
				else:
					parts[attr] = a
		
		if self.extra_fields:
			parts.update(self.extra_fields)
		
		return parts
	
	def as_json(self, rfc_fieldnames=False):
		return json.dumps(self.as_dict(rfc_fieldnames=rfc_fieldnames))
	
	
	# TYPECASTING
	def __repr__(self):
		return self.display_label
	
	def __str__(self):
		return self.__unicode__()
	
	def __unicode__(self):
		n = self.display_label
		if n:
			return unicode(n) # type:ignore
		elif self.city or self.state or self.country:
			return u'Unnamed - %s' % self.display_location
		else:
			return u'Unnamed'
	
	
	# LOGIC OPERATORS
	def __bool__(self):
		return self.is_valid
	
	def __nonzero__(self):
		return self.is_valid
	
	def __not__(self):
		return not self.is_valid
	
	def __eq__(self, other):
		if not isinstance(other, DN):
			return NotImplemented
		else:
			is_equal = True
			this_d = self.as_dict()
			that_d = other.as_dict()
			for k, v in this_d.iteritems():
				if that_d.get(k, None) != v:
					is_equal = False
			
			return is_equal
	
	def __ne__(self, other):
		return not self.__eq__(other)
