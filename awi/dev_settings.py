#	Lupinia Studios
#	By Natasha Long
#	www.lupinia.net - natasha@lupinia.net
#	
#	=================
#	Django Settings File
#	Everything in this first section is site-specific
#	=================

SITE_ID = 1
ADMIN_FOR = ('awi.fur_settings',)
WSGI_APPLICATION = 'awi.dev_wsgi.application'
DEBUG = True

from settings import *