#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings - App-Specific Config
#	Config options for apps that aren't part of Django
#	=================
import os

# Not external settings, but they're used in this file, so they need to be here.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATICFILES_DIRS = (os.path.abspath(os.path.join(BASE_DIR,'static/')),)
DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'

# Used as a "scratchpad" for operations that require local file storage.
WORKING_DIR = os.path.abspath(os.path.join(BASE_DIR,'working_dirs/'))

# Used as an "inbox" for operations that involve importing from local files regularly.
# NOTE:  It's recommended to put this outside the BASE_DIR, so that users uploading files don't need access to the code.
IMPORT_DIR = os.path.abspath('/srv/awi_import/')


#	CUSTOM APPS
#	==============
#	gridutils
#	This dictionary stores the settings for different types of Second Life/OpenSim objects
#	Use the app name and model name of the parent model to reference these.
#	Structure:
#		appname.modelname:
#			confirm_new:  If True, user attempting to initialize a new object will be required to login to the website to verify the request.
#			limit_duplicates:  If True, only one device of the same type per user may be rezzed in each region.
#			limit_move:  If True, the same object UUID with the same auth token in a different region will be blocked.  Otherwise, rezzing this device in a new region will update the existing device, deactivating the old one.
#			require_url:  If True, a valid remote URL for the in-world device will be expected and maintained.
#			wearable_allowed:  If True, instances of this device can have their "wearable" attribute set to True, which will bypass location checks entirely.  Use carefully!
#			auth_key_maxage:  Number of days to wait before the next request will cycle the auth key.
#			sync_age_yellow:  Number of days to wait before the sync health is a cause for concern (the "red" status is defined by timestamp_sync older than now - auth_key_maxage).
#			api_rate_limit:  Maximum number of queries per device per minute.
#			standard_fields:  Optional.  Follows the structure of DEVICE_API_STANDARD_FIELDS.
DEVICE_SETTINGS = {
	'gridutils.device': {	# Defaults
		'confirm_new': False,
		'limit_duplicates': False,
		'limit_move': True,
		'require_url': False,
		'wearable_allowed': False,
		'auth_key_maxage': 14,
		'sync_age_yellow': 7,
		'api_rate_limit': 30,
	},
	# DeerGuard
	'deerguard_sl.security_server': {
		'confirm_new': True,
		'limit_duplicates': False,
		'limit_move': True,
		'require_url': False,
		'wearable_allowed': False,
		'auth_key_maxage': 30,
		'sync_age_yellow': 14,
		'api_rate_limit': 60,
	},
}

#	Number of days in the future to expire an authorization token when replacing it
DEVICE_AUTH_DEPRECATION_DAYS = 365

#	Number of hours in the future to expire a device manual approval request after creating it
DEVICE_APPROVAL_REQUEST_MAXAGE = 24

#	Dictionary of required headers for device API requests, and more standardized internal names
DEVICE_API_REQUIRED_HEADERS = {
	'HTTP_X_SECONDLIFE_OBJECT_NAME': 'device_name',
	'HTTP_X_SECONDLIFE_OBJECT_KEY': 'device_key',
	'HTTP_X_SECONDLIFE_OWNER_NAME': 'owner_name',
	'HTTP_X_SECONDLIFE_OWNER_KEY': 'owner_key',
	'HTTP_X_SECONDLIFE_SHARD': 'grid_shard',
	'HTTP_X_SECONDLIFE_REGION': 'region_name',
	'HTTP_X_SECONDLIFE_LOCAL_POSITION': 'device_location',
}

#	Dictionary of expected POST fields for all device API requests, and whether they're required
#		If True, validation will fail without this field
DEVICE_API_STANDARD_FIELDS = {
	'auth_token': True,
	'object_auth': True,
	'group_owned': True,
	
	'is_attached': False,	# This shouldn't be present in most requests, but checking it anyway is useful for security
	'group_key': False,
	'owner_account_key': False,
	'previous_region_name': False,	# Only used for a corner case where a region is renamed
}

#	API rate limiting
DEVICE_API_RATELIMIT_CACHE_PREFIX = 'gudvcapi_devicereq_open'

#	Second Life API settings
SECONDLIFE_API_URL_N2A = 'https://api.secondlife.com/get_agent_id'
SECONDLIFE_API_RATELIMIT_CACHE_PREFIX = 'gudvcapi_slapi_open'
SECONDLIFE_GRIDSLUG = 'sl'

#	Vector type settings
VECTORTYPE_COORD_SPACING = True	# If True, vectors presented as strings will have a space after each comma


#	electionmap
ELECTION_PARTIES = (
	('I', 'Other/Independent'),
	('D', 'Democratic'),
	('R', 'Republican'),
	('d', 'Ind. (Dem Caucus)'),
	('r', 'Ind. (GOP Caucus)'),
	('X', 'Runoff'),
)

SENATE_CLASSES = (
	(0, 'None'),
	(1, 'Class 1'),
	(2, 'Class 2'),
	(3, 'Class 3'),
)


#	deertrees
#	This stores a list of known models that can be attached to a category, their hierarchy when displayed, and a template file's path
#	Model Name { 
#				title: Displayable title, OR an image URL relative to {{STATIC_PREFIX}}, OR False,
#				template: Path to importable template,
#				is_leaf: Boolean; if False, this entry is data for a block that isn't a leaf, but still has a foreign key to categories or tags, 
#				custom_obj: String; import path for a function that will be used for this block.  Use this for more complex queries, or content that doesn't have a foreign key to a category or tag, 
#				count: Integer; number of leaves per page to display for this leaf type.  Zero == unlimited
#				prefetch: List; if present, this adds fields to prefetch_related,
#				related: List; if present, this adds fields to select_related, }
DEERTREES_BLOCKS = {
	'image' : {'title':'Photography/Artwork', 'template':'sunset/leaf_image.html', 'is_leaf':True, 'count':100, 'prefetch':['assets',]},
	'page': {'title':'Writing', 'template':'deerbooks/leaf_page.html', 'is_leaf':True, 'count':50, 'related':['book_title',]},
	'link': {'title':'Links', 'template':'deerconnect/leaf_link.html', 'is_leaf':True, 'count':0,},
	'special_feature': {'title':'Special Features', 'template':'deertrees/leaf_feature.html', 'is_leaf':True, 'count':0,},
}

DEERTREES_BLOCKS_SPECIAL = {
	'category': {'title':'Subcategories', 'template':'deertrees/leaf_subcat.html', 'is_leaf':False, 'custom_obj':'deertrees.views.subcats', },
	'contact_link': {'title':'Contact Natasha', 'template':'deerconnect/leaf_contact_link.html', 'is_leaf':False, 'custom_obj':'deerconnect.views.contact_widget', },
	'category_thumb': {'title':'Subcategories', 'template':'deertrees/leaf_subcats_thumb.html', 'is_leaf':False, 'custom_obj':'deertrees.views.subcats', },
	'upcoming_events': {'title':'Upcoming Events', 'template':'deerattend/widget.html', 'is_leaf':False, 'custom_obj':'deerattend.views.widget', },
	'image_widget' : {'template':'sunset/image_widget.html', 'is_leaf':True, 'custom_obj':'sunset.views.recent_widget', },
	'image_folder_widget' : {'template':'sunset/folder_widget.html', 'is_leaf':False, 'custom_obj':'sunset.views.import_folder_widget', },
	'page_widget' : {'template':'deerbooks/page_widget.html', 'is_leaf':True, 'custom_obj':'deerbooks.views.recent_widget', },
}

#	This stores the block mapping options for categories and tags.
DEERTREES_BLOCK_MAP = {
	'default' : {
		'main_left' : ['image', 'page', 'category', 'link', ],
		'main_right' : ['page', 'category', 'link', 'image', ],
		'sidebar' : ['contact_link', 'special_feature', 'category', 'page', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Default'},
	},
	
	'image' : {
		'main' : ['image', 'category', 'page', 'link', ],
		'sidebar' : ['contact_link', 'special_feature', 'category', 'page', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Photos/Other Images'},
	},
	
	'image_split' : {
		'main_left' : ['image', ],
		'main_right' : ['category_thumb', ],
		'sidebar' : ['contact_link', 'special_feature', 'page', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Images with Image Subcategories (Split)'},
	},
	
	'page' : {
		'main' : ['page', 'category', 'link', ],
		'main_2' : ['image', ],
		'sidebar' : ['contact_link', 'page', 'special_feature', 'category', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Writing'},
	},
	
	'desc_split' : {
		'main_left' : 'desc',
		'main_right' : ['image', 'page', 'category', 'link', ],
		'sidebar' : ['contact_link', 'special_feature', 'category', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Description-Priority (Split)'},
	},
	
	'desc' : {
		'main' : 'desc',
		'main_2' : ['image', 'page', 'category', 'link', ],
		'sidebar' : ['contact_link', 'special_feature', 'category', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Description-Priority'},
	},
	
	'home' : {
		'main' : ['image', ],
		'main_2' : ['page', ],
		'sidebar' : ['upcoming_events', 'special_feature', 'link', ],
		'meta' : {'option_name': 'Homepage', 'selectable':False, },
	},
	
	'photo_root' : {
		'main_left' : ['category_thumb', ],
		'main_right' : ['image_widget', ],
		'sidebar' : ['contact_link', 'special_feature', 'page', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Photography (Root)'},
	},
	
	'page_root' : {
		'main_left' : ['page', 'page_widget', ],
		'main_right' : ['category', ],
		'sidebar' : ['contact_link', 'special_feature', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Writing (Root)'},
	},
	
	'code_root' : {
		'main_left' : ['page_widget', ],
		'main_right' : ['category', ],
		'sidebar' : ['contact_link', 'special_feature', 'page', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Code/Professional (Root)'},
	},
	
	'personal_root' : {
		'main_left' : 'desc',
		'main_right' : ['page', 'image', ],
		'sidebar' : ['category', 'contact_link', 'special_feature', 'link', 'upcoming_events', 'image_folder_widget', ],
		'meta' : {'option_name': 'Personal (Root)'},
	},
	
	'art_root' : {
		'main_left' : ['category_thumb', 'image', ],
		'main_right' : ['page', ],
		'sidebar' : ['contact_link', 'upcoming_events', 'special_feature', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Artwork (Root)'},
	},
	
	'char' : {
		'main' : 'desc',
		'main_2' : ['image', ],
		'sidebar' : ['contact_link', 'page', 'category', 'special_feature', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Character'},
	},
	
	'char_split' : {
		'main_left' : 'desc',
		'main_right' : ['image', ],
		'sidebar' : ['contact_link', 'page', 'category', 'special_feature', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Character (Split View)'},
	},
	
	'vehicle' : {
		'main_left' : ['image', ],
		'main_right' : ['page', 'category_thumb', ],
		'sidebar' : ['category', 'contact_link', 'special_feature', 'link', 'image_folder_widget', ],
		'meta' : {'option_name': 'Vehicle'},
	},
}


#	deerfind
#	Stores a list of apps and their associated finder functions, in the event of a 404
#	If DeerFind can't match the URL to a known-bad one, it will check these until it gets a True, or runs out.
#	Finder functions should return a tuple; first value boolean (match found), second value a string (empty if no match, root-relative URL if match)
#	Can be on a per-app basis, not necessarily per-model
#	Ordering based on frequency of use is recommended, for increased efficiency
DEERFIND_FINDERS = (
	'deerfind.views.g2_finder',
	'deerbooks.views.finder',
	'deertrees.views.finder',
	'sunset.views.finder',
)

#	Default fields used for main/simple search form.
DEERFIND_DEFAULT_SEARCH_FIELDS = [
	'title',
	'text',
	'tags',
	'summary',
]

#	Stores a dictionary of paths for search result templates for each indexed object.
#	Use the content type as the dictionary key.
SEARCH_RESULT_DATA = {
	'deerattend.event_instance': {'display_name': 'Event', 'default_icon':'event', },
	'deerattend.venue': {'display_name': 'Event Venue', 'default_icon':'place', },
	'deerbooks.page': {'display_name': 'Writing', 'default_icon':'book', 'template': 'deerbooks/content_thumb_page.html', },
	'deercoins.coin': {'display_name': 'Coin Collection', 'default_icon':'coin', },
	'deerconnect.contact_link': {'display_name': 'Contact Link', 'default_icon':'contact', },
	'deerconnect.link': {'display_name': 'External Link', 'default_icon':'link', },
	'deerfood.menu_item': {'display_name': 'Kitchen Menu', 'default_icon':'deerfood', },
	'deertrees.category': {'display_name': 'Category', 'default_icon':'category-misc', 'template': 'deertrees/content_thumb_deertrees.html', },
	'deertrees.tag': {'display_name': 'Tag', 'default_icon':'tag', 'template': 'deertrees/content_thumb_deertrees.html', },
	'sunset.image': {'display_name': 'Image', 'default_icon':'image', 'template': 'sunset/content_thumb_image.html', },
}
SEARCH_RESULT_TEMPLATE_DEFAULT = 'includes/content_thumb_default.html'

#	Shortcode model map
DEERFIND_SHORTCODE_TYPES = {
	'e': 'deerattend.event',
	'v': 'deerattend.venue',
	'p': 'deerbooks.page',
	'c': 'deertrees.category',
	't': 'deertrees.tag',
	'x': 'deertrees.special_feature',
	'i': 'sunset.image',
}


#	deerbooks
#	Specify location of a working directory for compiling LaTeX source files.
DEERBOOKS_CACHE_DIR = os.path.abspath(os.path.join(WORKING_DIR,'deerbooks/'))
DEERBOOKS_LATEX_CMD = ['/usr/bin/rubber','--ps','--pdf','--inplace']	# Command format for subprocess.check_output()


#	sunset
#	Specify the maximum sizes, and other processing settings, for various image_asset types.
#	Size format is (width,height)
#	watermark=True means that assets of this type will be watermarked.
#	exact=True means that assets of this type will be fitted to these exact dimensions.
SUNSET_IMAGE_ASSET_SIZES = {
	'icon':{'label':'Icon','size':(1500,250),'watermark':False,'exact':False,},
	'display':{'label':'Display-Resized Copy','size':(1280,960),'watermark':True,'exact':False,},
	'full':{'label':'Public Full-Size Image','size':(1920,1300),'watermark':True,'exact':False,},
	'bg':{'label':'Site Background','size':(1700,1000),'watermark':False,'exact':True,},
	'og':{'label':'OpenGraph Card Image','size':(1200,630),'watermark':True,'exact':True,},
	'twitter':{'label':'Twitter Card Image','size':(1200,600),'watermark':True,'exact':True,},
}

SUNSET_IMPORT_DIR = os.path.abspath(os.path.join(IMPORT_DIR,'sunset/'))
SUNSET_CACHE_DIR = os.path.abspath(os.path.join(WORKING_DIR,'sunset/'))
SUNSET_WATERMARK_IMAGE = os.path.abspath(os.path.join(BASE_DIR,'sunset/watermarks/lupinia.png'))
SUNSET_BG_NOTIFY_FAIL = True	# Send a notification if sunset_bg is used but a background image cannot be found.
SUNSET_EXIFTOOL_CMD = '/usr/bin/exiftool'	# ExifTool executable path for pyexiftool
SUNSET_RESYNC_TIME = 8	# Time before rechecking sync folders, measured in hours

#	New tab page view
#	Tuple of strings:
#		First value is the label that will be displayed
#		Second value is the actual timezone data for pytz
NEWTAB_CLOCK_LIST = [
	('Seattle', 'America/Los_Angeles'),
	('Lima', 'America/Lima'),
	('UTC', 'UTC'),
	('Baghdad', 'Asia/Baghdad'),
	('Karachi', 'Asia/Karachi'),
	('Perth', 'Australia/Perth'),
	('Adelaide', 'Australia/Adelaide'),
	('Sydney', 'Australia/Sydney'),
]


#	THIRD-PARTY APPS
#	==============
#	debug_toolbar
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
	#'debug_toolbar.panels.profiling.ProfilingPanel',
	'haystack_panel.panel.HaystackDebugPanel', 
	#'django_uwsgi.panels.UwsgiPanel', 
]


#	django_admin_tools
ADMIN_TOOLS_INDEX_DASHBOARD = 'awi.admin_tools_custom.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'awi.admin_tools_custom.CustomAppIndexDashboard'
ADMIN_TOOLS_MENU = 'awi.admin_tools_custom.CustomMenu'
ADMIN_TOOLS_THEMING_CSS = 'css/admin_tools.css'


#	haystack
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 50


#	s3_folder_storage
import boto.s3.connection
AWS_S3_CALLING_FORMAT = boto.s3.connection.OrdinaryCallingFormat()
AWS_S3_SECURE_URLS = True
AWS_QUERYSTRING_AUTH = False

DEFAULT_S3_PATH = 'awi'
STATIC_S3_PATH = 'awi-hagata'

# This is the default, but apparently I have to explicitly set it to silence a warning that shows up in EVERYTHING.  Thanks django-storages.
AWS_DEFAULT_ACL = None


#	static_precompiler
STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE = True
STATIC_PRECOMPILER_ROOT = os.path.abspath(os.path.join(STATICFILES_DIRS[0],'css/'))
STATIC_PRECOMPILER_OUTPUT_DIR = STATICFILES_DIRS[0]
STATIC_PRECOMPILER_COMPILERS = ( 
#	('static_precompiler.compilers.SCSS', {"executable": "/usr/local/bin/sassc", "compass_enabled": False}),
	('static_precompiler.compilers.libsass.SCSS', {
		"sourcemap_enabled": False,
		"precision": 8,
	}),
)

