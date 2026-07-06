#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for the Django Sites framework
#	=================

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.middleware import CurrentSiteMiddleware as CurrentSiteMiddlewareRaw
from django.core.cache import cache

SITE_CACHE_PREFIX = 'awi.utils.sites'

def get_site(pk=None):
	"""Retrieve a specific Site object from cache if possible"""
	if pk is None:
		pk = settings.SITE_ID
	
	target_site = cache.get('%s.%d' % (SITE_CACHE_PREFIX, pk))
	if target_site is None:
		target_site = Site.objects.filter(pk=pk).first()
		if target_site:
			cache.set('%s.%d' % (SITE_CACHE_PREFIX, target_site.pk), target_site, None)
			return target_site
		else:
			return None

def get_current_site(request=None):
	cur_site = cache.get('%s.%d' % (SITE_CACHE_PREFIX, settings.SITE_ID))
	if cur_site is None:
		cur_site = Site.objects.get_current()
		cache.set('%s.%d' % (SITE_CACHE_PREFIX, cur_site.pk), cur_site, None)
	
	return cur_site

def get_site_pks():
	pk_list = cache.get('%s.all.pklist' % SITE_CACHE_PREFIX)
	if pk_list is None:
		pk_list = list(Site.objects.all().values_list('pk', flat=True))
		cache.set('%s.all.pklist' % SITE_CACHE_PREFIX, pk_list, None)
	
	return pk_list

class CurrentSiteMiddleware(CurrentSiteMiddlewareRaw):
	"""
	Middleware that sets `site` attribute to request object, using cache if possible
	"""
	def process_request(self, request):
		request.site = get_current_site(request)
