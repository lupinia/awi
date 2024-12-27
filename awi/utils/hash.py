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
	hash = hashlib.md5(source)
	return hash.hexdigest()

def hash_sha1(source):
	hash = hashlib.sha1(source)
	return hash.hexdigest()

def hash_sha256(source):
	hash = hashlib.sha256(source)
	return hash.hexdigest()

def hash_sha512(source):
	hash = hashlib.sha512(source)
	return hash.hexdigest()
