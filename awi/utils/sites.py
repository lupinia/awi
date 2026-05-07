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

def get_cache_prefix(pk):
	return '%s.%d' % (SITE_CACHE_PREFIX, pk)

def get_current_site(request=None):
	cur_site = cache.get(get_cache_prefix(settings.SITE_ID))
	if cur_site is None:
		cur_site = Site.objects.get_current()
		cache.set(get_cache_prefix(cur_site.pk), cur_site, None)
	
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
