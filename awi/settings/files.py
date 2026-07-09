#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Files
#	Filesystem and file management settings
#	=================

import os

# =================
#	Base File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Used as a "scratchpad" for operations that require local file storage.
WORKING_DIR = os.path.abspath(os.path.join(BASE_DIR,'working_dirs/'))

# Used as an "inbox" for operations that involve importing from local files regularly.
# NOTE:  It's recommended to put this outside the BASE_DIR, so that users uploading files don't need access to the code.
IMPORT_DIR = os.path.abspath('/srv/awi_import/')


# =================
#	Sunset
#	Local working directory for image editing and metadata extraction.
SUNSET_CACHE_DIR = os.path.abspath(os.path.join(WORKING_DIR,'sunset/'))

# Local storage directories for original images
SUNSET_IMPORT_DIR = os.path.abspath(os.path.join(IMPORT_DIR,'sunset/'))
SUNSET_UPLOAD_DIR = os.path.abspath(os.path.join(SUNSET_IMPORT_DIR,'web_upload/'))

# Watermark path
SUNSET_WATERMARK_IMAGE = os.path.abspath(os.path.join(BASE_DIR,'sunset/watermarks/lupinia.png'))

# ExifTool executable path for pyexiftool
SUNSET_EXIFTOOL_CMD = '/usr/bin/exiftool'

# Email admins if sunset_bg is used but a background image cannot be found.
SUNSET_BG_NOTIFY_FAIL = True

# Time before rechecking sync folders, measured in hours
SUNSET_RESYNC_TIME = 8

# Specify the maximum sizes, and other processing settings, for various image_asset types.
#	Size format is (width,height)
#	watermark=True means that assets of this type will be watermarked.
#	exact=True means that assets of this type will be fitted to these exact dimensions.
#	exact=False means that images are resized proportionally to fit inside the smallest dimension
SUNSET_IMAGE_ASSET_SIZES = {
	'icon':{
		'label':'Icon',
		'size':(1500,250),
		'watermark':False,
		'exact':False,
	},
	'display':{
		'label':'Display-Resized Copy',
		'size':(1280,960),
		'watermark':True,
		'exact':False,
	},
	'full':{
		'label':'Public Full-Size Image',
		'size':(1920,1300),
		'watermark':True,
		'exact':False,
	},
	'bg':{
		'label':'Site Background',
		'size':(1700,1000),
		'watermark':False,
		'exact':True,
	},
	'og':{
		'label':'OpenGraph Card Image',
		'size':(1200,630),
		'watermark':True,
		'exact':True,
	},
	'twitter':{'label':'Twitter Card Image','size':(1200,600),'watermark':True,'exact':True,},
}


# =================
#	DeerBooks
#	Specify location of a working directory for compiling LaTeX source files.
DEERBOOKS_CACHE_DIR = os.path.abspath(os.path.join(WORKING_DIR,'deerbooks/'))

# Command format for subprocess.check_output()
DEERBOOKS_LATEX_CMD = ['/usr/bin/rubber','--ps','--pdf','--inplace']


# =================
#	Core Media/Static Settings
MEDIA_URL = 'https://cdn.fur.vc/awi/'
STATIC_URL = 'https://cdn.fur.vc/awi-hagata/'

DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'

STATICFILES_DIRS = (
	os.path.abspath(os.path.join(BASE_DIR,'static/')),
)

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	
	'static_precompiler.finders.StaticPrecompilerFinder',
)


# =================
#	S3 Storage
AWS_S3_SECURE_URLS = True
AWS_QUERYSTRING_AUTH = False

DEFAULT_S3_PATH = 'awi'
STATIC_S3_PATH = 'awi-hagata'

# This is the default, but apparently I have to explicitly set it
# to silence a warning that shows up in EVERYTHING.
# Thanks django-storages.
AWS_DEFAULT_ACL = None


# =================
#	Static Precompiler
STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE = True
STATIC_PRECOMPILER_ROOT = os.path.abspath(os.path.join(STATICFILES_DIRS[0],'css/'))
STATIC_PRECOMPILER_OUTPUT_DIR = STATICFILES_DIRS[0]
STATIC_PRECOMPILER_COMPILERS = ( 
	('static_precompiler.compilers.libsass.SCSS', {
		"sourcemap_enabled": False,
		"precision": 8,
	}),
)
