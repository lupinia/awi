#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Local
#	This information is sensitive and should not be committed to Github.
#	=================

#	EXAMPLE, CHANGE ALL INFO BEFORE RUNNING

# =================
#	IP Addresses
#	At the top for easier editing
INTERNAL_IPS = ('',)


# =================
#	Credentials
SECRET_KEY = ''

# AWS and S3
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
AWS_S3_CUSTOM_DOMAIN = ''

# Mapbox
MAPBOX_KEY = ''

# Second Life name-to-agent API
# https://wiki.secondlife.com/wiki/Name_to_agent_ID_API
SECONDLIFE_API_URL_N2A = ''
SECONDLIFE_API_KEY = ''


# =================
#	Email
ADMINS = (('', ''),)
MANAGERS = ADMINS
SERVER_EMAIL = ''

DEFAULT_FROM_EMAIL = ''
EMAIL_HOST = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = ''

DEERCONNECT_TO_EMAIL = ''


# =================
#	General/Misc
SERVER_CANONICAL_NAME = ''
ALLOWED_HOSTS = ['',]

# Honeypots
HONEYPOT_FIELD_NAME = ''
HONEYPOT_FIELD_NAME_AWIACCESS = ''

# User IDs
SITE_OWNER_ACCOUNT_ID = 0
CLI_DEFAULT_ACCOUNT_ID = 0

# User agent string for DeerConnect health check
DEERCONNECT_HEALTHCHECK_USERAGENT = ''


# =================
#	Infrastructure
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2', 
		'NAME': '',
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	},
}

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
		'LOCATION': '',
	},
}

HAYSTACK_CONNECTIONS = {
	'default': {
		'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',
		'URL': '',
		'INDEX_NAME': 'haystack_awi',
		'INCLUDE_SPELLING':True,
		'KWARGS': {
			'use_ssl': True,
			'verify_certs': True,
		},
	},
}


# =================
#	x.509 Auth
#	Server headers for mTLS authentication, since those are server-specific
X509_HEADER_IS_ENFORCED = ''
X509_HEADER_VERIFICATION = ''
X509_HEADER_FINGERPRINT = ''
X509_HEADER_SUBJECT = ''
X509_HEADER_DATE_EXPIRY = ''
X509_HEADER_DATE_START = ''
X509_HEADER_SERIALNUM = ''
X509_HEADER_ISSUER = ''
