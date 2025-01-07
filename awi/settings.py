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

MEDIA_URL = 'https://cdn.fur.vc/awi/'
STATIC_URL = 'https://cdn.fur.vc/awi-hagata/'
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
	'django.contrib.humanize',
	'django.contrib.sitemaps',
	
	#	Third-party apps
	'cookielaw', 
	'debug_toolbar',
	'haystack', 'haystack_panel', 
	'honeypot',
	'mptt', 'django_mptt_admin',
	's3_folder_storage',
	'static_precompiler',
	
	#	My Apps - System/Core
	'awi_access',	# Access Control
	'deerfind',		# Intelligent 404 Recovery
	'watchdeer',	# Unified logging and notifications
	
	#	My Apps - Primary Content Objects
	'deerbooks',	# Text-based content
	'deerconnect',	# Link directory and contact form/links
	'deertrees',	# Categories
	'sunset',		# Photo/image gallery
	
	#	My Apps - Second Life Systems/Content
	'gridutils',	# Base models and tools for virtual world data management
	'deerguard_sl',	# Access control for Second Life objects/scripts
	#'deerland',		# Virtual world estate/property management
	'deerbuild',	# Second Life creator tools and project support
	'electionmap',	# Election results data tracking and visualization
	
	#	My Apps - Other
	'deerattend',	# Convention/event database
	'deercoins',	# Coin collection database
	'deerfood',		# Restaurant-style menu
	'deersky',		# Digital almanac and weather/timezone data aggregation
)

#	System Settings
TEMPLATES = [{
	'BACKEND': 'django.template.backends.django.DjangoTemplates',
	'DIRS' : [os.path.abspath(os.path.join(BASE_DIR,'./templates')),],
	'OPTIONS' : {
		'context_processors' : [
			'django.contrib.auth.context_processors.auth',
			'django.template.context_processors.debug',
			'django.template.context_processors.i18n',
			'django.template.context_processors.media',
			'django.template.context_processors.static',
			'django.template.context_processors.tz',
			'django.contrib.messages.context_processors.messages',
			
			#	Non-standard ones
			'django.template.context_processors.request',
			'awi.context_processors.site',
			'awi.context_processors.settings_vars',
			'awi.context_processors.meta',
			'awi_access.context_processors.mature_check',
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
	'debug_toolbar.middleware.DebugToolbarMiddleware',
)

middleware_main = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.sites.middleware.CurrentSiteMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

middleware_cache_update = ('django.middleware.cache.UpdateCacheMiddleware',)
middleware_cache_fetch = ('django.middleware.cache.FetchFromCacheMiddleware',)
#	End Middleware

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
		},
	},
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'filters': ['require_debug_false'],
			'class': 'django.utils.log.AdminEmailHandler'
		},
		'null': {
			'class': 'logging.NullHandler',
		},
	},
	'loggers': {
		'django.security.DisallowedHost': {
			'handlers': ['null',],
			'propagate': False,
		},
		'django.security.BadRequest': {	# It's very stupid that this actually works
			'handlers': ['null',],
			'propagate': False,
		},
		'django.request': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': True,
		},
	}
}
