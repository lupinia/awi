#	GridUtils - Virtual World Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	====================
#	Custom Type: Vector
#	====================

import math
import re

from django.conf import settings

from awi.utils.types import is_iterable, is_string

vector_types = {
	'float':'float',		# Default, can be anything
	'int':'int',			# Unbounded, but no decimal
	'percent':'percent',	# min -1, max 1, float
	'axis':'bool',			# True/False, interpreted in LSL as integers 1/0
	
	'prim_size':'float',	# min 0.01, max 64
	'position':'float',		# min 0, max 256x256x4096
	'pos_local':'float',	# min -64, max 64
	'color':'percent',		# min 0, max 1
	'angle':'float',		# min 0, max 360
	'mapurl':'int',			# int version of position
	'direction':'percent',	# min -1, max 1
	'tex_scale':'float',	# min 0, max unbounded, no Z
	'tex_offset':'percent',	# min -1, max 1, no Z
}

# HELPER FUNCTIONS
# Special vector handling for strings
# Accepts <>, [], or () as enclosing characters
# Doesn't do validation, just deconstructs the format
# Always returns three values, None indicates failure
def coords_from_string(input):
	input = input.strip().replace(" ", "")
	if input == "ZERO_VECTOR":
		return (0, 0, 0)
	
	parse_match = re.search(r"(?:<|\[|\()(?P<x>\S+?),(?P<y>\S+?),(?P<z>\S+?)(?:>|\]|\))", input)
	if parse_match is None:
		return (None, None, None)
	else:
		return (parse_match.group('x'), parse_match.group('y'), parse_match.group('z'))

# Special vector handling for lists and tuples
# Doesn't do validation, just deconstructs the format
# Always returns three values, None indicates failure
def coords_from_iter(input):
	if len(input) == 1:
		# Only one element, so just apply it to all three coordinates
		input.extend([input[0], input[0]])
	elif len(input) == 2:
		# Two elements, so append a zero to make it three
		input.append(0)
	
	if len(input) == 3:
		# We're good to go!
		return input
	else:
		# Not sure what this is, but it's not a vector
		return (None, None, None)

# Decorator for math operators
def _operator(func):
	def inner(this, other):
		if isinstance(other, vector):
			# Working with something that's already a vector, so just send it directly
			return func(this, other)
		elif type(other) in [int, float, bool]:
			# This could easily be turned into a vector, so convert and then send
			return func(this, type(this)(other))
		elif is_string(other) or isinstance(other, dict) or other is None:
			# For other numeric types, explicit type conversion is needed for interacting with strings
			# So we'll do that here too
			# Dicts and None will also fail automatically here
			return NotImplemented
		elif is_iterable(other) and len(other) == 3:
			# I'll allow you to do this if it's exactly 3 elements
			return func(this, type(this)(other))
		else:
			# What even is this?
			return NotImplemented
	
	return inner


# CLASS DEFINITIONS
class vector(object):
	"""
	Defines a 3-axis set of coordinates or parameters for use as a single unit.
	Primarily useful in 3D modeling, and especially heavily used in Second Life.
	Cast to string formatted as <x,y,z>.
	Not an iterable, treated as a number for math operations. 
	
	Attributes:
		x (float):  X axis, or all 3 axes if no other coordinates are supplied
		y (float):  Y axis
		z (float):  Z axis, optional
	
	Typecasting to vector:
		From strings:
			Strings should be three numbers enclosed in <> to cast to vector
			However, string representations of lists or tuples will also work
			You shouldn't do this intentionally (see From iterables)
				vector('<1.04563, 3.9, 7.0>') -> <1.04563, 3.9, 7.0>
				vector('[1.04563, 3.9, 7.0]') -> <1.04563, 3.9, 7.0>
				vector('(1.04563, 3.9, 7.0)') -> <1.04563, 3.9, 7.0>
			Special string ZERO_VECTOR will be cast to <0,0,0> for compatibility with LSL scripts:
				vector('ZERO_VECTOR') -> <0,0,0>
			Numbers represented as strings in any axis/argument () will be treated as numbers:
				vector("1", "2", "3") -> <1,2,3>
		From float/int/Decimal and other numbers:
			Single numbers will be added to all three axes when cast to vector:
				vector(1) -> <1,1,1>
		From bools:
			Boolean values True and False will be treated as the numbers 1 and 0 for LSL compatibility:
				vector(True) -> <1,1,1>
				vector(False, True, False) -> <0,1,0>
		From NoneType:
			None passed as a coordinate will raise a TypeError, to maintain consistency with Python standards.
				vector(None) -> TypeError: 'NoneType' object is not a number
		From dicts:
			Dictionaries cast to vector will raise a TypeError; use ** to unpack them instead
				vector({"x":1, "y":2, "z":3}) -> TypeError: 'dict' object is not a number
				vector(**{"x":1, "y":2, "z":3}) -> <1,2,3>
		From iterables:
			Iterables of 3 elements or less should be unpacked using * instead of casting directly
			However, since they resemble a stock-Python representation of a vector,
			and they could get interpreted this way by JSON parsing, typecasting will work. 
			Casting a list or tuple to vector will be treated as positional arguments, so same rules apply. 
			This is primarily to help with serialization bugs, please don't do this intentionally. 
				vector(*[1, 2, 3]) -> <1,2,3>
				vector([1, 2, 3]) -> <1,2,3>
				vector([1, 2]) -> <1,2,0>
				vector([1]) -> <1,1,1>
	
	Operators:
		Vectors generally behave like single numbers for the purposes of math operations.
			<1, 2, 3> + <1, 1, 1> returns <2, 3, 4>
			<1, 2, 3> - <1, 1, 1> returns <0, 1, 2>
			<1, 2, 3> * <2, 2, 2> returns <2, 4, 6>
			<1, 2, 3> ** <2, 2, 2> returns <1, 4, 9>
			<2, 4, 6> / <2, 2, 2> returns <1, 2, 3>
			etc.
		All operators against a single number will perform the specified operation against all three coordinates
			Example:  <1, 2, 3> + 1 returns <2, 3, 4>
			NOTE:
				This behavior differs from LSL, which treats vectors more like mathematical arrays:
				LSL only allows cross-product or dot multiplication, and does not support division.
				While this behavior makes sense for things like velocity,
				it's not useful for most non-physics use-cases of vectors (which is most of them).
				And since this is a Python class meant to supplement LSL scripts, not replace them,
				simply operating on all three axes separately is more useful here.
		Operators against objects that can be typecast to a vector will implicitly do so.
			Example:  <1, 2, 3> * "<2, 2, 2>" returns <2, 4, 6>
			However, lists, tuples, and other iterables will only be implicitly typecast
			if they contain exactly three elements.  Otherwise, they must be explicitly cast to vector.
			This is because iterables are vague and not necessarily a vector, but are the only other way
			to represent vector-like data in Python.
			So, an iterable of exactly three elements can safely be assumed to be a vector.
		Comparison operators separately compare all three coordinates.
			For example, in a greater than check, at least one coordinate
			must be greater than, and none can be less than.
			<1, 2, 4> > <1, 2, 3> returns True
			<0, 2, 4 > <1, 2, 3> returns False
		Equality checks all three coordinates equal to each other
			<1, 2, 3> == <1, 2, 3> returns True
			<1, 2, 3> == <3, 2, 1> returns False
			<1, 2, 3> == <1, 1, 1> returns False
				This can be tested with vector.any_equal(num)
	"""
	
	prec = 5	# Maximum decimal places when representing as a string
	
	# Coordinates!  The main thing we're here for!
	# At least I assume that's what you're here for
	# If you're not here for coordinates, you may have come to the wrong class
	# Only three dimensions for now.  Extradimensional geometry coming soon.
	x = 0
	y = 0
	z = 0
	
	def __init__(self, *args, **kwargs):
		"""
		vector(x, y, z, type='float') -> Create a new vector object
		Flexible to accommodate data normalization issues between LSL scripts and Python APIs.
		All coordinates are optional, and can be keyword or positional arguments.
		Keyword arguments will always apply the value only to a specified axis.
		Positional arguments will make some assumptions:
			If only one coordinate is given, it will be applied to all three axes:
				vector(1) -> <1,1,1>
				This is equivalent to typecasting a single number
				This is also required for math operations like <3,4,5> + 1 to make sense
				If you're passing one argument and it must only be the X axis, use a keyword argument
			If only two coordinates are given, they will be treated as X and Y, and Z will be zero:
				vector(1,2) -> <1,2,0>
			If all three coordinates are given, they will be treated as X, Y, and Z:
				vector(1,2,3) -> <1,2,3>
		
		Parameters:
			x: X axis coordinate
			y: Y axis coordinate
			z: Z axis coordinate
			validate: Optional, set to False to disable vector.validate_coords() on creation
		"""
		# This code *could* be a lot simpler, but it would be less accurate/flexible
		# LSL is a hot mess, so ingesting its output requires a lot of flexibility
		need_x = True
		need_y = True
		need_z = True
		validate = True
		kwarg_coords = False
		
		# Let's start with the kwargs, because they're easy
		if 'x' in kwargs.keys():
			self.x = kwargs.pop('x', self.x)
			need_x = False
			kwarg_coords = True
		
		if 'y' in kwargs.keys():
			self.y = kwargs.pop('y', self.y)
			need_y = False
			kwarg_coords = True
		
		if 'z' in kwargs.keys():
			self.z = kwargs.pop('z', self.z)
			need_z = False
			kwarg_coords = True
		
		if 'validate' in kwargs.keys():
			validate = kwargs.pop('validate', True)
		
		if args and any([need_x, need_y, need_z]):
			# Ok, we still have positional arguments to deal with
			# And we still *need* positional arguments, so let's parse them!
			args = list(args)
			if len(args) == 1:
				if all([need_x, need_y, need_z]):
					# If we're here, we're typecasting, so this could be anything
					# Step 1:  The easiest is converting one type of vector to another
					if isinstance(args[0], vector):
						# Re-normalizing *should* be a formality, but that's the main difference between vector types
						self.x = args[0].x
						self.y = args[0].y
						self.z = args[0].z
						args = []	# Blank the list since we're not popping
						need_x = False
						need_y = False
						need_z = False
					
					# Step 2:  Handle the easy ones
					elif args[0] == "ZERO_VECTOR" or args[0] is False:
						# Literally the name of a constant in the LSL standard library
						# Also handle casting bool False the same way
						self.set_to_zero()
						args = []	# Blank the list since we're not popping
						need_x = False
						need_y = False
						need_z = False
					elif args[0] is True:
						# Casting bool True to integer 1
						self.set_to_value(1)
						args = []	# Blank the list since we're not popping
						need_x = False
						need_y = False
						need_z = False
					
					# Step 3:  If it's a dict, fail immediately
					elif isinstance(args[0], dict):
						raise TypeError('cannot cast dict to vector')
					
					# Step 4:  This could be a string representation of multiple values
					elif is_string(args[0]):
						coords_check = coords_from_string(args.pop(0))
						if None in coords_check:
							raise TypeError('casting str to vector requires 3 comma-separated coordinates')
						else:
							self.x, self.y, self.z = coords_check
							need_x = False
							need_y = False
							need_z = False
					
					# Step 5:  Perhaps it's an iterable?
					elif is_iterable(args[0]):
						coords_check = coords_from_iter(args.pop(0))
						if None in coords_check:
							raise TypeError('casting iterable to vector requires 3 elements')
						else:
							self.x, self.y, self.z = coords_check
							need_x = False
							need_y = False
							need_z = False
					
					# Step 6:  If we're here, we'll treat this as a single value
					else:
						self.set_to_value(args.pop(0))
						need_x = False
						need_y = False
						need_z = False
				
				else:
					# Received a mixture of args and kwargs, neat
					# Please don't do this
					if need_x:
						self.x = args.pop(0)
						need_x = False
					elif need_y:
						self.y = args.pop(0)
						need_y = False
					elif need_z:
						self.z = args.pop(0)
						need_z = False
			
			elif len(args) == 2:
				if all([need_x, need_y, need_z]):
					# Just a 2D coordinate pair living in a 3D world
					self.x, self.y = args
					self.z = False
					args = []	# Blank the list since we're not popping
					need_x = False
					need_y = False
					need_z = False
				else:
					# ...Seriously?
					if need_x and args:
						self.x = args.pop(0)
						need_x = False
					
					if need_y and args:
						self.y = args.pop(0)
						need_y = False
					
					if need_z and args:
						self.z = args.pop(0)
						need_z = False
			
			elif len(args) == 3:
				if all([need_x, need_y, need_z]):
					# OMG thank you for actually following instructions!
					# ...At least I assume you did. Figuring that out is someone else's job.
					self.x, self.y, self.z = args
					args = []	# Blank the list since we're not popping
					need_x = False
					need_y = False
					need_z = False
				else:
					# What did you even DO here?  What IS this?
					# Like, ok, so you sent me exactly three positional arguments.
					# Cool!  Awesome!  That's exactly what I wanted!
					# ...But you ALSO explicitly set one or more coordinates in kwargs?
					# So, then, what are we even still doing here?  And what are these args?
					# I would love to know what actually happened here.  This *fascinates* me.
					# But I can't find out, so, here's your exception.  Enjoy it.  Cherish it. 
					raise TypeError('Indecypherable or duplicate coordinates for vector()')
			
			else:
				# Ma'am this is a Wendy's
				raise TypeError('vector() can only accept 3 coordinates')
		
		
		# Ok!  Let's see if we figured it out
		if any([need_x, need_y, need_z]) and not kwarg_coords:
			# Uh, I think we're missing some pieces here...
			raise TypeError('Unable to parse vector input into 3 coordinates')
		
		# Final cleanup!  We have our values, let's see if they work
		self.normalize_coords()
		if validate:
			self.validate_coords()
		
		super(vector, self).__init__(*args, **kwargs)
	
	
	# INITIALIZATION
	# Reset this to zero, but leave other values intact
	def set_to_zero(self):
		self.set_to_value(0)
	
	def set_to_value(self, new_value):
		self.x = new_value
		self.y = new_value
		self.z = new_value
	
	
	# VALIDATION AND NORMALIZATION
	def normalize_coord(self, coord):
		"""
		vector.normalize_coord(coord) -> float(coord)
		Convert a single coordinate value to a float, or raises a value error.
		Should be overridden by child classes that require different number types.
		"""
		return float(coord)
	
	def normalize_coords(self):
		"""
		Bulk method to normalize all three coordinates
		Overriding this is not recommended, override normalize_coord() instead
		"""
		if None in [self.x, self.y, self.z]:
			raise ValueError("'NoneType' object is not a number")
		
		self.x = self.normalize_coord(self.x)
		self.y = self.normalize_coord(self.y)
		self.z = self.normalize_coord(self.z)
	
	def validate_coords(self):
		"""
		Apply validation rules to coordinates.  Does nothing by default.
		Should be extended by child classes for different types of vectors.
		"""
		pass
	
	
	# OUTPUT
	def coord_as_string(self, coord, pad=False):
		"""
		vector.coord_as_string(coord, pad) -> str(coord)
		Convert a single coordinate value to a string.
		Number of allowed decimal places is set in vector.prec attribute
		
		Parameters:
			coord: The numeric value to be converted
			pad: If True, add trailing zeros to ensure the correct number of decimal places
		"""
		coord = str(coord)
		if self.prec:
			if '.' in coord:
				i, d = coord.split('.')
				d = d[:self.prec]
				if len(d) < self.prec and pad:
					d = d.ljust(self.prec, '0')
				coord = '%s.%s' % (i, d)
			else:
				coord = coord + '.'.ljust(self.prec+1, '0')
		elif '.' in coord:
			coord, d = coord.split('.')
		
		return coord
	
	def as_string(self, pad=False):
		"""
		Format output as a string.
		Optional parameter "pad" adds trailing spaces
		to ensure the correct number of decimal places if True
		"""
		return '<%s,%s%s,%s%s>' % (
			self.coord_as_string(self.x, pad),
			self.spacer,
			self.coord_as_string(self.y, pad),
			self.spacer,
			self.coord_as_string(self.z, pad)
		)
	
	def as_list(self):
		"""
		Retrieve coordinates as a list.
		vector is not an iterable, so this is a typecasting method, like vector.as_string()
		"""
		return [self.x, self.y, self.z]
	
	@property
	def spacer(self):
		"""
		Shortcut for checking coordinate spacing and conditionally inserting a space between commas.
		"""
		if getattr(settings, 'VECTORTYPE_COORD_SPACING', False):
			return ' '
		else:
			return ''
	
	def __repr__(self):
		return self.as_string(pad=False)
	
	def __str__(self):
		return self.as_string(pad=True)
	
	def __unicode__(self):
		return self.as_string(pad=True)
	
	
	# SPECIAL OPERATIONS
	# Check if any coordinate matches the specified number
	def any_equal(self, other):
		"""
		vector.any_equal(number) -> True or False
		Check whether number is equal to any coordinate in this vector
		"""
		return any([self.x==other, self.y==other, self.z==other])
	
	# Calculate distance
	def distance(self, other):
		"""
		vector.distance(vector) -> float
		Calculates the distance between this vector and another vector
		Based on llVecDist():  https://wiki.secondlife.com/wiki/LlVecDist
		"""
		difference = self - other
		return difference.magnitude
	
	# Calculate magnitude
	@property
	def magnitude(self):
		"""
		vector.magnitude -> float
		Contains the calculated magnitude of this vector
		Based on llVecMag():  https://wiki.secondlife.com/wiki/LlVecMag
		"""
		return math.sqrt(sum([self.x*self.x, self.y*self.y, self.z*self.z]))
	
	# Calculate normal
	@property
	def normal(self):
		"""
		vector.normal -> vector
		Contains a calculated vector indicating the normalized direction of this vector
		Based on llVecNorm():  https://wiki.secondlife.com/wiki/LlVecNorm
		"""
		return self / self.magnitude
	
	def floor(self):
		"""Converts all coordinates to integers, rounded down"""
		return type(self)(x=math.floor(self.x), y=math.floor(self.y), z=math.floor(self.z))
	
	def ceil(self):
		"""Converts all coordinates to integers, rounded up"""
		return type(self)(x=math.ceil(self.x), y=math.ceil(self.y), z=math.ceil(self.z))
	
	def round(self, prec=None):
		"""
		vector.round(prec) -> vector
		Returns a copy of this vector with all three coordinates rounded to the number of decimal places specified in prec
		Defaults to the precision specified in the class definition for this vector type
		"""
		if prec is None:
			prec = self.prec
		return type(self)(x=round(self.x, prec), y=round(self.y, prec), z=round(self.z, prec))
	
	
	# MATH OPERATORS
	# Addition
	@_operator
	def __add__(self, other):
		return type(self)(x=self.x+other.x, y=self.y+other.y, z=self.z+other.z)
	
	def __radd__(self, other):
		return self.__add__(other)
	
	# Subtraction
	@_operator
	def __sub__(self, other):
		return type(self)(x=self.x-other.x, y=self.y-other.y, z=self.z-other.z)
	
	@_operator
	def __rsub__(self, other):
		return type(self)(x=other.x-self.x, y=other.y-self.y, z=other.z-self.z)
	
	# Multiplication
	@_operator
	def __mul__(self, other):
		return type(self)(x=self.x*other.x, y=self.y*other.y, z=self.z*other.z)
	
	def __rmul__(self, other):
		return self.__mul__(other)
	
	# Division
	@_operator
	def __div__(self, other):
		return type(self)(x=self.x/other.x, y=self.y/other.y, z=self.z/other.z)
	
	@_operator
	def __rdiv__(self, other):
		return type(self)(x=other.x/self.x, y=other.y/self.y, z=other.z/self.z)
	
	def __truediv__(self, other):
		return self.__div__(other)
	
	def __rtruediv__(self, other):
		return self.__rdiv__(other)
	
	@_operator
	def __mod__(self, other):
		return type(self)(x=self.x%other.x, y=self.y%other.y, z=self.z%other.z)
	
	def __rmod__(self, other):
		# This one *only* makes sense if other is a vector
		if isinstance(other, vector):
			return type(self)(x=other.x%self.x, y=other.y%self.y, z=other.z%self.z)
		else:
			return NotImplemented
	
	@_operator
	def __floordiv__(self, other):
		return type(self)(x=self.x//other.x, y=self.y//other.y, z=self.z//other.z)
	
	@_operator
	def __rfloordiv__(self, other):
		return type(self)(x=other.x//self.x, y=other.y//self.y, z=other.z//self.z)
	
	# Other
	def __abs__(self):
		return type(self)(x=abs(self.x), y=abs(self.y), z=abs(self.z))
	
	def __neg__(self):
		return type(self)(x= -self.x, y= -self.y, z= -self.z)
	
	def __pos__(self):
		return -self.__neg__()
	
	@_operator
	def __pow__(self, other):
		return type(self)(x=self.x**other.x, y=self.y**other.y, z=self.z**other.z)
	
	def __rpow__(self, other):
		# This one *only* makes sense if other is a vector
		if isinstance(other, vector):
			return type(self)(x=other.x**self.x, y=other.y**self.y, z=other.z**self.z)
		else:
			return NotImplemented
	
	
	# LOGIC OPERATORS
	def __bool__(self):
		return any(self.as_list())
	
	def __nonzero__(self):
		return self.__bool__()
	
	def __not__(self):
		return not self.__bool__()
	
	@_operator
	def __lt__(self, other):
		return any([
			self.x<other.x,
			self.y<other.y,
			self.z<other.z
		]) and not any([
			self.x>other.x,
			self.y>other.y,
			self.z>other.z,
		])
	
	@_operator
	def __le__(self, other):
		return any([
			self.x<=other.x,
			self.y<=other.y,
			self.z<=other.z,
		]) and not any([
			self.x>other.x,
			self.y>other.y,
			self.z>other.z,
		])
	
	@_operator
	def __gt__(self, other):
		return any([
			self.x>other.x,
			self.y>other.y,
			self.z>other.z,
		]) and not any([
			self.x<other.x,
			self.y<other.y,
			self.z<other.z,
		])
	
	@_operator
	def __ge__(self, other):
		return any([
			self.x>=other.x,
			self.y>=other.y,
			self.z>=other.z,
		]) and not any([
			self.x<other.x,
			self.y<other.y,
			self.z<other.z,
		])
	
	@_operator
	def __eq__(self, other):
		return all([self.x==other.x, self.y==other.y, self.z==other.z])
	
	@_operator
	def __ne__(self, other):
		return not self.__eq__(other)


# OTHER VECTOR TYPES
class ivector(vector):
	"""
	Special type of vector strictly used for integers
	"""
	prec = 0
	
	def normalize_coord(self, coord):
		"""
		vector.normalize_coord(coord) -> int(coord)
		Convert a single coordinate value to an integer, or raises a value error.
		"""
		return int(coord)
