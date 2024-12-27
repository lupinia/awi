#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for randomness operations
#	=================

import random
import string

#	Generate a random integer sequence of a specific length.
#		duplicates:  Boolean.  If True, sequential duplicates are allowed.
#		first_zero:  Boolean.  If True, first digit in sequence can be a zero.
#		exclude_zero:  Boolean.  If True, no zeros will be part of the sequence.
#		exclude:  List.  If present, the specified digits will not be part of the sequence.
def rand_int_list(length=1, duplicates=False, first_zero=False, exclude_zero=False, exclude=[]):
	# Handle bad inputs, just in case
	if length < 1:
		return []
	elif length > 1024:
		length = 1024
	
	generator = random.SystemRandom()
	int_list = []
	i = 0
	while i < length:
		if exclude_zero:
			range_start = 1
		elif not first_zero and not i:
			range_start = 1
		else:
			range_start = 0
		int_list.append(generator.randrange(range_start, 10))
		i += 1
		
		# Check for sequential duplicates
		if duplicates == False and i > 1:
			if int_list[i-1] == int_list[i-2]:
				int_list.pop()
				i -= 1
		
		# Check for exclusion
		if int_list[i-1] in exclude:
			int_list.pop()
			i -= 1
	
	return int_list

#	Generate a random letter sequence of a specific length.
#		duplicates:  Boolean.  If True, sequential duplicates are allowed.
#		mix_case:  Boolean.  If True, both upper and lowercase letters will be included.  Else, only uppercase will be returned.
#		exclude:  List.  Any characters in this list will be removed from the possible selections, case-insensitively.
#		include_digits:  Boolean.  If True, numbers will also be added to the selection pool.
#		first_zero:  Boolean.  If True, first digit in sequence can be a zero.  Only has an effect if include_digits is also true.
def rand_char_list(length=1, duplicates=False, mix_case=False, exclude=[], include_digits=False, first_zero=False):
	# Handle bad inputs, just in case
	if length < 1:
		return []
	elif length > 1024:
		length = 1024
	
	# Set up the initial range
	if mix_case:
		char_range = string.ascii_letters
	else:
		char_range = string.ascii_uppercase
	
	if include_digits:
		char_range += '0123456789'
	
	for ex in exclude:
		char_range = char_range.replace(ex.lower(), '')
		char_range = char_range.replace(ex.upper(), '')
	
	generator = random.SystemRandom()
	char_list = []
	i = 0
	
	while i < length:
		char_list.append(generator.choice(char_range))
		i += 1
		
		# Check for sequential duplicates
		if duplicates == False and i > 1:
			if char_list[i-1].lower() == char_list[i-2].lower():
				char_list.pop()
				i -= 1
		elif not first_zero and i == 1:
			if char_list[0] == '0':
				char_list.pop()
				i -= 1
	
	return char_list
