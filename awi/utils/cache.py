#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for caching
#	=================

from django.core.cache import cache as default_cache_obj

# Abstract model base classes and mixin classes
class ModelCacheMixin(object):
	"""
	Special model mixin for model-level caching.
	Adds all standard cache API methods, prefixed with cache_*:
		cache_get, cache_set, cache_get_or_set, etc
	
	Adds the following additional attributes: 
		CLEAR_CACHE_ON_SAVE:  Bool, automatically clears persistent keys on model save
		objcache_id:  Property, make sure this returns a unique value per object
	
	Adds the following additional custom methods:
		cache_key(key):  Returns an object-prefixed version of the given key, or None
		cache_keys(keys):  Many version of cache_key, prefixes every element in the list
		cache_clear(*extra_keys):  Clear all persistent keys just for this object, and any others
		objcache_persistent_keys(*extra_keys):  Build a list of persistent keys for this object (override in models)
	"""
	CLEAR_CACHE_ON_SAVE = True
	
	# Key handling
	@property
	def objcache_id(self):
		"""
		Unique prefix to use for this object in the cache
		Override for models that inherit this mixin
		Ensure this always has a unique value when it's in use
		"""
		return None
	
	def cache_key(self, key):
		"""
		Return a prefixed version of the given key.
		Returns None if objcache_id is None
		"""
		if self.objcache_id:
			return '%s.%s' % (self.objcache_id, key)
		else:
			return None
	
	def cache_keys(self, keylist):
		"""
		Return a prefixed version of the given key.
		Returns an empty list if objcache_id is None
		"""
		if self.objcache_id and keylist:
			return [self.cache_key(x) for x in keylist]
		else:
			return []
	
	
	# Custom operations
	def cache_clear(self, *extra_keys):
		"""
		Clear the persistent cache for this object
		Relies on the list contained in .objcache_persistent_keys()
		"""
		keylist = self.objcache_persistent_keys(*extra_keys)
		if keylist:
			default_cache_obj.delete_many(keylist)
	
	def objcache_persistent_keys(self, *extra_keys):
		"""Retrieve a list of persistent keys to clear when resetting the cache for this object"""
		if self.objcache_id is None:
			return None
		
		keylist = []
		if len(extra_keys):
			keylist = keylist + extra_keys
		
		return self.cache_keys(keylist)
	
	
	# Standard cache methods
	def cache_get(self, key, fallback=None):
		"""
		Proxy for cache.get(), with a prefixed key unique to this object
		Include a fallback value other than None to get a default
		"""
		return default_cache_obj.get(self.cache_key(key), fallback)
	
	def cache_set(self, key, value, timeout=None):
		"""
		Proxy for cache.set(), with a prefixed key unique to this object
		Defaults to permanent, set timeout for an expiration time
		"""
		if self.objcache_id:
			default_cache_obj.set(self.cache_key(key), value, timeout)
	
	def cache_get_or_set(self, key, default, timeout=None):
		"""
		Proxy for cache.get_or_set(), with a prefixed key unique to this object
		Defaults to permanent, set timeout for an expiration time
		"""
		if self.objcache_id:
			return default_cache_obj.get_or_set(self.cache_key(key), default, timeout)
		else:
			return default
	
	def cache_get_many(self, keys, fallback={}):
		"""
		Proxy for cache.get_many(), with prefixed keys unique to this object
		Include a fallback value other than None to get a default
		"""
		if self.objcache_id:
			return default_cache_obj.get_many(self.cache_keys(keys))
		else:
			return fallback
	
	def cache_set_many(self, data, timeout=None):
		"""
		Proxy for cache.set_many(), with prefixed keys unique to this object
		Defaults to permanent, set timeout for an expiration time
		"""
		if self.objcache_id and data:
			newdata = {}
			for rawkey, val in data.iteritems():
				newdata[self.cache_key(rawkey)] = val
			
			default_cache_obj.set_many(newdata, timeout)
	
	def cache_delete(self, key):
		"""Proxy for cache.delete(), with a prefixed key unique to this object"""
		if self.objcache_id:
			default_cache_obj.delete(self.cache_key(key))
	
	def cache_delete_many(self, keys):
		"""Proxy for cache.delete_many(), with prefixed keys unique to this object"""
		if self.objcache_id:
			default_cache_obj.delete_many(self.cache_keys(keys))
	
	def cache_touch(self, key, timeout=None):
		"""Proxy for future cache.touch(), to renew a key's expiration date without altering it"""
		if hasattr(default_cache_obj, 'touch'):
			return default_cache_obj.touch(self.cache_key(key), timeout)
		else:
			curval = self.cache_get(self.cache_key(key))
			if curval is None:
				return False
			else:
				self.cache_set(self.cache_key(key), curval, timeout)
				return True
	
	
	# System methods and overrides
	def save(self, *args, **kwargs):
		if self.CLEAR_CACHE_ON_SAVE and self.objcache_id:
			self.cache_clear()
		
		super(ModelCacheMixin, self).save(*args, **kwargs)
