#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Main
#	Primary Django settings
#	=================

from settings_core import *
from settings_local import *
from settings_apps import *

ALLOWED_HOSTS = ['*',]
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE = 'chr'		# Cherokee translation for Django is in progress, but not ready yet!
#LOCALE_PATHS = (os.path.abspath(os.path.join(BASE_DIR,'./locale')),)

STATICFILES_DIRS = (os.path.abspath(os.path.join(BASE_DIR,'./static')),)
MEDIA_URL = 'http://cdn.fur.vc/awi/'
STATIC_URL = 'http://cdn.fur.vc/awi-hagata/'
#	Moved STATICFILES_STORAGE and DEFAULT_FILE_STORAGE to settings_apps because they're used in other apps' settings

SECURE_CONTENT_TYPE_NOSNIFF = True
LOGIN_REDIRECT_URL='/'
ROOT_URLCONF = 'awi.urls'

INSTALLED_APPS = (
	'django.contrib.contenttypes',
	
	#	Admin Tools (Has to go first)
	'admin_tools', 'admin_tools.theming', 'admin_tools.menu', 'admin_tools.dashboard',
	
	#	System Items
	'django.contrib.auth', 'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin', 'django.contrib.admindocs',
	
	#	Third-party apps
	'mptt', 'django_mptt_admin',
	's3_folder_storage',
	'django_summernote',
	'django_processinfo',
	'debug_toolbar',
	
	#	My Apps - System/Core
	'deerfind',		# 404 Map
	'awi_error',	# Error Handling
	'awi_access',	# Access Control
	'awi_bg',		# Backgrounds
	'secondlife',
	
	#	My Apps - Primary Content Objects
	'deertrees',	# Categories
	'deerbooks',	# Text-based content
	'deerconnect',	# Link directory and contact form/links
	
	#	My Apps - Other
	'deerhealth',	# Prescription Tracker
)

#	System Settings
TEMPLATES = [{
	'BACKEND': 'django.template.backends.django.DjangoTemplates',
	'DIRS' : [os.path.abspath(os.path.join(BASE_DIR,'./templates')),],
	'OPTIONS' : {
		'context_processors' : [
			'django.contrib.auth.context_processors.auth',
			'django.core.context_processors.debug',
			'django.core.context_processors.i18n',
			'django.core.context_processors.media',
			'django.core.context_processors.static',
			'django.template.context_processors.tz',
			'django.contrib.messages.context_processors.messages',
			
			#	Non-standard ones
			'django.core.context_processors.request',
			'awi.context_processors.site',
			'deerconnect.context_processors.social_icons',
		],
		'loaders' : [
			#	It's really stupid that I have to add a custom template loader for django-admin-tools.
			#	Might be looking for a new alternative.
			
			'django.template.loaders.filesystem.Loader',
			('django.template.loaders.cached.Loader', ['django.template.loaders.app_directories.Loader',],),
			
			'admin_tools.template_loaders.Loader',
		],
	},
},]

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
		'LOCATION': 'dbcache',
	}
}

MIDDLEWARE_CLASSES = (
	'django_processinfo.middlewares.django_processinfo.ProcessInfoMiddleware',
	'debug_toolbar.middleware.DebugToolbarMiddleware',
	
	#'django.middleware.cache.UpdateCacheMiddleware',
	
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	
	#'django.middleware.cache.FetchFromCacheMiddleware',
)
