#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Local
#	This information is sensitive and should not be committed to Github.
#	=================

#	EXAMPLE, CHANGE ALL INFO BEFORE RUNNING

ADMINS = (('', ''),)
MANAGERS = ADMINS
SITE_OWNER_ACCOUNT_ID = 1
SERVER_CANONICAL_NAME = ''

INTERNAL_IPS = ('',)
ALLOWED_HOSTS = ['',]
HONEYPOT_FIELD_NAME = ''
HONEYPOT_FIELD_NAME_AWIACCESS = ''

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
AWS_S3_CUSTOM_DOMAIN = ''

EMAIL_HOST = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = ''
SERVER_EMAIL = ''
DEFAULT_FROM_EMAIL = ''

DEERCONNECT_TO_EMAIL = ''
DEERCONNECT_HEALTHCHECK_USERAGENT = ''

SECRET_KEY = ''	# Make this unique, and don't share it with anybody.

MAPBOX_KEY = ''
SECONDLIFE_API_KEY = ''	# For name-to-agent API

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2', 
		'NAME': '',
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
		'LOCATION': '',
	}
}

HAYSTACK_CONNECTIONS = {
	'default': {
		'ENGINE': 'haystack.backends.elasticsearch_backend.Elasticsearch2SearchEngine',
		'URL': '',
		'INDEX_NAME': 'haystack_awi',
		'INCLUDE_SPELLING':True,
		'KWARGS': {
			'use_ssl': True,
			'verify_certs': True,
		}
	},
}

