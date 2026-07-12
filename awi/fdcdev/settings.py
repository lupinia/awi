#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Site (Frolicking Deer Cay)
#	
#	Site-specific Django settings
#	=================

from awi.settings import *

SITE_ID = 3
WSGI_APPLICATION = 'awi.fdcdev.wsgi.application'
DEBUG = True

#	Dev-specific URL overrides
ROOT_URLCONF = 'awi.fdcdev.urls'

#	Site-specific metadata values and defaults
SITE_TITLE = 'Frolicking Deer Cay'
SITE_TITLE_IMG_CODE = 'fr' # Set to 'fr' unless you know what this does
DEFAULT_AUTHOR_NAME = 'Natasha L.'
DEFAULT_AUTHOR_TWITTER = '@lupinia'
DEFAULT_AUTHOR_MASTODON = '@lupinia@infosec.exchange'

#	Middleware got a little interesting, to get the caching middleware inserted in the correct order, but not on the dev server.
MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES
