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
WSGI_APPLICATION = 'awi.prod.wsgi.application'
DEBUG = False

#	Site-specific metadata values and defaults
SITE_TITLE = 'Lupinia Studios'
SITE_TITLE_IMG_CODE = 'fr' # Set to 'fr' unless you know what this does
DEFAULT_AUTHOR_NAME = 'Natasha L.'
DEFAULT_AUTHOR_TWITTER = '@lupinia'
DEFAULT_AUTHOR_MASTODON = '@lupinia@infosec.exchange'

from awi.settings import *

#	Middleware got a little interesting, to get the caching middleware inserted in the correct order, but not on the dev server.
middleware_first = ()
MIDDLEWARE_CLASSES = middleware_first + middleware_cache_update + middleware_main + middleware_cache_fetch