#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Main
#	Primary Django settings
#	=================

import os
from settings_local import *
from settings_apps import *

USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE = 'chr'		# Cherokee translation for Django is in progress, but not ready yet!
#LOCALE_PATHS = (os.path.abspath(os.path.join(BASE_DIR,'./locale')),)

STATICFILES_DIRS = (os.path.abspath(os.path.join(BASE_DIR,'static/')),)
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR,'devCSS/'))
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
	'static_precompiler',
	
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
	'deerfood',		# Restaurant-style menu
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
			'django.template.loaders.app_directories.Loader',
			
			'admin_tools.template_loaders.Loader',
		],
	},
},]

#	Middleware got a little interesting, to get the caching middleware inserted in the correct order, but not on the dev server.
middleware_first = (
	'django_processinfo.middlewares.django_processinfo.ProcessInfoMiddleware',
	'debug_toolbar.middleware.DebugToolbarMiddleware',
)

middleware_main = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

middleware_cache_update = ('django.middleware.cache.UpdateCacheMiddleware',)
middleware_cache_fetch = ('django.middleware.cache.FetchFromCacheMiddleware',)
#	End Middleware

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
		'LOCATION': 'dbcache',
	}
}

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	
	'static_precompiler.finders.StaticPrecompilerFinder',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}