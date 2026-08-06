#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Core/Misc
#	Primary Django settings, and settings that don't have a more specific file
#	=================

# =================
#	Localization
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'


# =================
#	Sessions/Auth/Security
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
CSRF_USE_SESSIONS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
LOGIN_REDIRECT_URL = '/'
AUTH_PASSWORD_VALIDATORS = [
	{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
	{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
	{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
		'OPTIONS': {'min_length': 12,},
	},
]


# =================
#	Django Admin Tools
ADMIN_TOOLS_INDEX_DASHBOARD = 'awi.admin_tools_custom.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'awi.admin_tools_custom.CustomAppIndexDashboard'
ADMIN_TOOLS_MENU = 'awi.admin_tools_custom.CustomMenu'
ADMIN_TOOLS_THEMING_CSS = 'css/admin_tools.css'


# =================
#	Debug Toolbar
DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_PANELS = [
	'debug_toolbar.panels.versions.VersionsPanel',
	'debug_toolbar.panels.timer.TimerPanel',
	'debug_toolbar.panels.settings.SettingsPanel',
	'debug_toolbar.panels.headers.HeadersPanel',
	'debug_toolbar.panels.request.RequestPanel',
	'debug_toolbar.panels.sql.SQLPanel',
	#'debug_toolbar.panels.staticfiles.StaticFilesPanel',
	'debug_toolbar.panels.templates.TemplatesPanel',
	'debug_toolbar.panels.cache.CachePanel',
	'debug_toolbar.panels.signals.SignalsPanel',
	'debug_toolbar.panels.logging.LoggingPanel',
	'debug_toolbar.panels.redirects.RedirectsPanel',
	'debug_toolbar.panels.profiling.ProfilingPanel',
	'haystack_panel.panel.HaystackDebugPanel', 
	#'django_uwsgi.panels.UwsgiPanel', 
]


# =================
#	GridUtils
SECONDLIFE_API_RATELIMIT_CACHE_PREFIX = 'gudvcapi_slapi_open'
SECONDLIFE_GRIDSLUG = 'sl'

#	If True, vectors presented as strings will have a space after each comma
VECTORTYPE_COORD_SPACING = True


# =================
#	Notifications
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
		'django.security.BadRequest': {
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
