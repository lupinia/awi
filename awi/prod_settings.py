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