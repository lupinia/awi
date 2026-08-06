#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings
#	
#	Objects referenced here but defined in other settings files:
#		import os (settings_apps)
#		BASE_DIR (settings_apps)
#	=================

# Importing all the other setting files
from .core import *
from .electionmap import *
from .files import *
from .frontend import *
from .lslapi import *
from .routing import *
from .search import *
from .secrets import *

# =================
#	App Config
INSTALLED_APPS = [
	'django.contrib.contenttypes',
	
	#	Admin Tools (Has to go first)
	'admin_tools', 'admin_tools.theming', 'admin_tools.menu', 'admin_tools.dashboard',
	
	#	System Items
	'django.contrib.auth', 'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin', 'django.contrib.admindocs',
	'django.contrib.humanize',
	'django.contrib.sitemaps',
	
	#	Third-party apps
	'debug_toolbar',
	'haystack', 'haystack_panel', 
	'honeypot',
	'mptt', 'django_mptt_admin',
	's3_folder_storage',
	'static_precompiler',
	
	#	My Apps - System/Core
	'dagasi',	# Access Control
]
