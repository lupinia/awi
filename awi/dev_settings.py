#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Site (Development)
#	
#	Site-specific Django settings
#	=================

SITE_ID = 1
ADMIN_FOR = ('awi.fur_settings',)
WSGI_APPLICATION = 'awi.dev_wsgi.application'
DEBUG = True

from settings import *

#	Middleware got a little interesting, to get the caching middleware inserted in the correct order, but not on the dev server.
middleware_cache_update = ()
middleware_cache_fetch = ()
MIDDLEWARE_CLASSES = middleware_first + middleware_cache_update + middleware_main + middleware_cache_fetch