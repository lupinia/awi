#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Site (Production)
#	
#	Site-specific Django settings
#	=================

SITE_ID = 1
ADMIN_FOR = ('awi.fur_settings',)
WSGI_APPLICATION = 'awi.prod_wsgi.application'
DEBUG = False

from settings import *

#	Middleware got a little interesting, to get the caching middleware inserted in the correct order, but not on the dev server.
MIDDLEWARE_CLASSES = middleware_first + middleware_cache_update + middleware_main + middleware_cache_fetch