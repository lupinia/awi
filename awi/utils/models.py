#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for Django models
#	=================

#	Since Django is stupidly picky about what it will accept for model field choices, 
#	I have to write a function that will turn the output of .keys() from a dict into tuple pairs.
def dict_key_choices(source_dict):
	keys = source_dict.keys()
	tuple_list = []
	
	for key in keys:
		tuple_list.append((key, key))
	
	return tuple_list
