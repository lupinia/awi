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

INTERNAL_IPS = ('',)
ALLOWED_HOSTS = ['',]
HONEYPOT_FIELD_NAME = ''

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''

EMAIL_HOST = ''
EMAIL_SUBJECT_PREFIX = ''
SERVER_EMAIL = ''
DEFAULT_FROM_EMAIL = ''
DEERCONNECT_TO_EMAIL = ''

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
SECRET_KEY = ''	# Make this unique, and don't share it with anybody.

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

