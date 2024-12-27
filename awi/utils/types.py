#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for type checking and casting
#	Normally, I'm all for duck typing, but sometimes that's just not good enough.
#	=================

def is_iterable(test_obj):
	try:
		type_test = iter(test_obj)
	except TypeError:
		return False
	else:
		return True

def is_int(test_obj):
	try:
		type_test = int(test_obj)
	except ValueError:
		return False
	except TypeError:
		return False
	else:
		return True

def is_string(test_obj):
	return isinstance(test_obj, basestring) # type: ignore
