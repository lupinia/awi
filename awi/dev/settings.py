#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Site (Development)
#	
#	Site-specific Django settings
#	=================

from awi.settings import *

SITE_ID = 1
WSGI_APPLICATION = 'awi.dev.wsgi.application'
DEBUG = True

#	Site-specific metadata values and defaults
SITE_TITLE = 'Lupinia Studios (Dev)'
SITE_TITLE_IMG_CODE = 'fr' # Set to 'fr' unless you know what this does
DEFAULT_AUTHOR_NAME = 'Natasha L.'
DEFAULT_AUTHOR_TWITTER = '@lupinia'
DEFAULT_AUTHOR_MASTODON = '@lupinia@infosec.exchange'

#	No caching middleware on the dev server, but we need the debug toolbar
MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES
