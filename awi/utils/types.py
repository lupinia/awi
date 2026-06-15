#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for type checking and casting
#	Normally, I'm all for duck typing, but sometimes that's just not good enough.
#	=================

def is_iterable(test_obj):
	"""
	is_iterable(obj) -> bool
	Tests whether an unknown object is iterable without an exception
	Always returns True (if yes) or False
	"""
	try:
		type_test = iter(test_obj)
	except TypeError:
		return False
	else:
		return True

def is_int(test_obj):
	"""
	is_int(obj) -> bool
	Tests whether an unknown object is - or can become - an integer without an exception
	Always returns True (if yes) or False
	"""
	try:
		type_test = int(test_obj)
	except ValueError:
		return False
	except TypeError:
		return False
	else:
		return True

def is_string(test_obj):
	"""
	is_string(obj) -> bool
	Tests whether an unknown object is a string
	Compatible with Python 2.7 unicode and str types
	Always returns True (if yes) or False
	"""
	return isinstance(test_obj, basestring) # type: ignore
