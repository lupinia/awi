#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Main
#	Primary Django settings
#	
#	Objects referenced here but defined in other settings files:
#		import os (settings_apps)
#		BASE_DIR (settings_apps)
#	=================

# =================
# Localization
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'

# =================
# URL Config
SECURE_CONTENT_TYPE_NOSNIFF = True
LOGIN_REDIRECT_URL='/'
ROOT_URLCONF = 'awi.urls'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

MEDIA_URL = 'https://cdn.fur.vc/awi/'
STATIC_URL = 'https://cdn.fur.vc/awi-hagata/'
#	Moved STATICFILES_STORAGE and DEFAULT_FILE_STORAGE to settings_apps because they're used in other apps' settings

# =================
# App Config
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
	'debug_toolbar',
	'haystack', 'haystack_panel', 
	'honeypot',
	'mptt', 'django_mptt_admin',
	's3_folder_storage',
	'static_precompiler',
	
	#	My Apps - System/Core
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
	'dagasi',	# Access Control
)

# =================
# Template Config
TEMPLATES = [{
	'BACKEND': 'django.template.backends.django.DjangoTemplates',
	'DIRS' : [
		os.path.abspath(os.path.join(BASE_DIR,'./templates/showcase')),	# Per-theme directory
		os.path.abspath(os.path.join(BASE_DIR,'./templates/global')),	# Templates for all themes
	],
	'OPTIONS' : {
		'context_processors' : [
			'awi.context_processors.core',
			
			'django.contrib.auth.context_processors.auth',
			'django.template.context_processors.debug',
			'django.template.context_processors.i18n',
			'django.template.context_processors.tz',
			'django.contrib.messages.context_processors.messages',
			
			#	Non-standard ones
			'awi.context_processors.site',
			'awi.context_processors.meta',
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

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	
	'static_precompiler.finders.StaticPrecompilerFinder',
)

# =================
# Middleware Config

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'dagasi.middleware.UserPrefsMiddleware',
	'awi.utils.sites.CurrentSiteMiddleware',
	'awi.utils.cache.CacheKeyPrefixMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


# =================
# Logging Config
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
