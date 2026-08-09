#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for hash operations
#	=================

import hashlib

#	More compact version of using hashlib to generate various types of hashes from strings
def hash_md5(source):
	"""Calculate an MD5 hash of an input string"""
	hash = hashlib.md5(source)
	return hash.hexdigest()

def hash_sha1(source):
	"""Calculate an SHA1 hash of an input string"""
	hash = hashlib.sha1(source)
	return hash.hexdigest()

def hash_sha256(source):
	"""Calculate an SHA256 hash of an input string"""
	hash = hashlib.sha256(source)
	return hash.hexdigest()

def hash_sha512(source):
	"""Calculate an SHA512 hash of an input string"""
	hash = hashlib.sha512(source)
	return hash.hexdigest()
