﻿#	GridUtils - Virtual World Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions
#	=================

import math

from django.conf import settings
from django.db import models

from awi_utils.utils import dict_key_choices, hash_sha1, hash_sha256

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

def format_vector(x, y, z):
	return '<%d, %d, %d>' % (x, y, z)

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
