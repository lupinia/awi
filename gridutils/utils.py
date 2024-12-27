#	GridUtils - Virtual World Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions
#	=================

import math
import requests

from django.conf import settings
from django.core.cache import cache
from django.db import models

from awi.utils.hash import hash_sha1, hash_sha256
from awi_utils.utils import dict_key_choices

# Use the Second Life Name-To-Agent API to validate a new username
# http://wiki.secondlife.com/wiki/Name_to_agent_ID_API
# Returns a tuple; first value is a pass/fail boolean or None on error, second is a status message
def verify_sl_name(user, new_name):
	status = None
	error = 'unknown'
	if getattr(settings, 'SECONDLIFE_API_KEY', ''):
		if user.grid.slug == settings.SECONDLIFE_GRIDSLUG:
			ratelimit_key = '%s:%s' % (settings.SECONDLIFE_API_RATELIMIT_CACHE_PREFIX, settings.SECONDLIFE_API_KEY)
			if cache.get(ratelimit_key):
				error = 'over_limit'
			else:
				cache.set(ratelimit_key, 1, 1)
				api_headers = {'api-key': settings.SECONDLIFE_API_KEY,}
				payload = {}
				if ' ' in new_name:
					payload['username'], payload['lastname'] = new_name.split(' ', 1)
				else:
					payload['username'] = new_name
					payload['lastname'] = 'Resident'
				
				try:
					r = requests.post(url=settings.SECONDLIFE_API_URL_N2A, headers=api_headers, json=payload)
					response_data = {}
					if r.status_code == 200 or r.status_code == 404:
						response_data = r.json()
					
					if r.status_code == 200:
						if response_data.get('agent_id', None) == user.key_str:
							status = True
							error = 'success'
						else:
							status = False
							error = 'key_mismatch'
					elif r.status_code == 403:
						error = 'rate_limited'
					elif r.status_code == 404:
						error = response_data.get('error', '')
						if error != 'invalid_api_key':
							status = False
							error = 'name_invalid'
					elif r.status_code == 500:
						error = 'remote_server_error'
				except requests.exceptions.RequestException:
					error = 'requests_error'
		else:
			error = 'wrong_grid'
	else:
		error = 'api_key_missing'
	
	return (status, error)

def coord_normalize(value, type='location'):
	if value < 0:
		return 0
	elif type == 'square' and value > 4096:
		return 4096
	elif type == 'location' and value > 256:
		return 256
	elif type == 'rotation' and value > 359:
		return 0
	else:
		return value

# TO DO:  Support different grids with this function
def format_slurl(sim_name, x=128, y=128, z=0):
	sim_name = sim_name.replace(' ', '%20')
	return 'https://maps.secondlife.com/secondlife/%s/%d/%d/%d' % (sim_name, x, y, z)

# Convert a set of three numbers (integers or floats) to SL's vector data type
def format_vector(x, y, z):
	return '<%d, %d, %d>' % (x, y, z)

# Convert an SL vector (represented as a string) to three separate numbers
# Valid inputs are '<x, y, z>' or '(x, y, z)' (spacing is irrelevant)
# Returns a tuple containing the extracted x, y, and z values.
# If the input string is invalid, the resulting values will all be zeros
def parse_vector(vector):
	x = 0.0
	y = 0.0
	z = 0.0
	
	# First, let's get rid of extra characters
	vector_normalized = vector.replace('(', '').replace(')', '').replace('<', '').replace('>', '').replace(' ', '')
	
	# We should now have a string containing three comma-separated numbers
	vector_list_raw = vector_normalized.split(',')
	if len(vector_list_raw) == 3:
		vector_list = []
		for i in vector_list_raw:
			# This really should be easier.  I hate Python type conversion.
			try:
				if '.' in i:
					n = float(i)
				else:
					n = int(i)
			except ValueError:
				# Whatever, just skip this one
				n = 0
			vector_list.append(n)
	
	return vector_list

# Converting between region coordinates and sequentially-numbered parcel border squares
# Counting starts from southwest corner; X is left to right, Y is bottom to top
# Why? Because that's how SL does it for some reason.
# The Z axis is irrelevant, but most coordinates in this system are stored/used as triples, so it's accepted for convenience.
# NOTE: This is inaccurate for coordinates that fall precisely on a border line.
def coords_to_square(x, y, z=0):
	x = coord_normalize(int(math.round(x/4, 0)))
	y = coord_normalize(int(math.round(y/4, 0)))
	
	if y <= 1:
		return x
	else:
		grid_y = (y-1) * 64
		return grid_y + x

def square_to_coords(s):
	s = coord_normalize(s, 'square')
	
	if s <= 1:
		result_x = 1
		result_y = 1
	else:
		result_x = s % 64
		result_y = int(math.ceil(s/64.0))
	
	x = (result_x * 4) - 2
	y = (result_y * 4) - 2
	
	return [x, y]

# Standard hash assembly method for auth functions for the in-world objects API
# Takes an arbitrary number of strings, assembles them as pipe-separated values
# Then returns an SHA1 hash of the result
# All values must already be strings!
def psv_hash(*args):
	psv = '|'.join(args)
	return hash_sha1(psv)

# More secure hash method for hashes that don't need to be assembled by LSL scripts
def psv_hash256(*args):
	psv = '|'.join(args)
	return hash_sha256(psv)

#	It's really dumb and annoying that I have to do this, and I can't just directly use .keys()
def device_type_choices():
	return dict_key_choices(settings.DEVICE_SETTINGS)

# Functions for working with our proprietary (but hopefully easy-to-parse) API format:
#	Key/value pairs are separated by $$
#	Keys are separated from values by |
def dict_to_apipsv(input={}):
	output_list = []
	for key, value in input:
		output_list.append(u'%s|%s' % (key, unicode(value))) # type: ignore
	
	return '$$'.join(output_list)

def parse_apipsv(input=''):
	parsed = {}
	elements = input.split('$$')
	if len(elements) > 0:
		for element in elements:
			pair = element.split('|', )
			if len(pair) > 1:
				parsed[pair[0]] = pair[1]
	
	return parsed

#	==================
#	Abstract Models

#	Base class for all models that represent a grid location
class location_model(models.Model):
	location_x = models.SmallIntegerField(default=0, blank=True, verbose_name='X')
	location_y = models.SmallIntegerField(default=0, blank=True, verbose_name='Y')
	location_z = models.SmallIntegerField(default=0, blank=True, verbose_name='Z')
	
	@property
	def x(self):
		return coord_normalize(self.location_x)
	
	@property
	def y(self):
		return coord_normalize(self.location_y)
	
	@property
	def z(self):
		return coord_normalize(self.location_z)
	
	@property
	def coords_list(self):
		return [self.x, self.y, self.z]
	
	@property
	def coords_vector(self):
		return format_vector(*self.coords_list)
	
	@property
	def coords_text(self):
		return '(%d, %d)' % (self.x, self.y)
	
	@property
	def slurl(self):
		if hasattr(self, 'region'):
			return self.get_location_slurl(self.region)
		else:
			return None
	
	def get_location_slurl(self, sim=None):
		if sim and hasattr(sim, 'name'):
			return format_slurl(sim.name, self.x, self.y, self.z)
		else:
			return None
	
	def get_location_text(self, sim=None):
		if sim and hasattr(sim, 'name'):
			region_name = sim.name
		else:
			region_name = 'Unknown'
		
		return '%s %s' % (region_name, self.coords_text)
	
	class Meta:
		abstract = True
