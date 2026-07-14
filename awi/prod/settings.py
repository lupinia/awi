#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Site (Production)
#	
#	Site-specific Django settings
#	=================

from awi.settings import *

SITE_ID = 1
WSGI_APPLICATION = 'awi.prod.wsgi.application'
DEBUG = False

#	Site-specific metadata values and defaults
SITE_TITLE = 'Lupinia Studios'
SITE_TITLE_IMG_CODE = 'fr' # Set to 'fr' unless you know what this does
DEFAULT_AUTHOR_NAME = 'Natasha L.'
DEFAULT_AUTHOR_TWITTER = '@lupinia'
DEFAULT_AUTHOR_MASTODON = '@lupinia@infosec.exchange'

DEFAULT_THEME = 'showcase'
DEFAULT_THEME_COLOR = 'purple'

#	Middleware got a little interesting, to get the caching middleware inserted in the correct order, but not on the dev server.
MIDDLEWARE_CLASSES = ('django.middleware.cache.UpdateCacheMiddleware',) + MIDDLEWARE_CLASSES + ('django.middleware.cache.FetchFromCacheMiddleware',)
