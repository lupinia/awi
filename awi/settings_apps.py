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


#	CUSTOM APPS
#	==============
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
	'image' : {'title':'Photography/Artwork', 'template':'sunset/leaf_image.html', 'is_leaf':True, 'count':50, 'prefetch':['assets',]},
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
	'page_widget' : {'template':'deerbooks/page_widget.html', 'is_leaf':True, 'custom_obj':'deerbooks.views.recent_widget', },
}

DEERTREES_BLOCK_MAP = {
	'default' : {
		'main_left' : ['image', 'page', 'category', 'link', ],
		'main_right' : ['page', 'category', 'link', 'image', ],
		'sidebar' : ['contact_link', 'special_feature', 'category', 'page', 'link', ],
		'meta' : {'option_name': 'Default'},
	},
	
	'image' : {
		'main' : ['image', 'category', 'page', 'link', ],
		'sidebar' : ['contact_link', 'special_feature', 'category', 'page', 'link', ],
		'meta' : {'option_name': 'Photos/Other Images'},
	},
	
	'image_split' : {
		'main_left' : ['image', ],
		'main_right' : ['category_thumb', ],
		'sidebar' : ['contact_link', 'special_feature', 'page', 'link', ],
		'meta' : {'option_name': 'Images with Image Subcategories (Split)'},
	},
	
	'page' : {
		'main' : ['page', 'category', 'link', ],
		'main_2' : ['image', ],
		'sidebar' : ['contact_link', 'page', 'special_feature', 'category', 'link', ],
		'meta' : {'option_name': 'Writing'},
	},
	
	'desc_split' : {
		'main_left' : 'desc',
		'main_right' : ['image', 'page', 'category', 'link', ],
		'sidebar' : ['contact_link', 'special_feature', 'category', 'link', ],
		'meta' : {'option_name': 'Description-Priority (Split)'},
	},
	
	'desc' : {
		'main' : 'desc',
		'main_2' : ['image', 'page', 'category', 'link', ],
		'sidebar' : ['contact_link', 'special_feature', 'category', 'link', ],
		'meta' : {'option_name': 'Description-Priority'},
	},
	
	'home' : {
		'main' : ['image', ],
		'main_2' : ['page', ],
		'sidebar' : ['special_feature', 'link', 'upcoming_events', ],
		'meta' : {'option_name': 'Homepage', 'selectable':False, },
	},
	
	'photo_root' : {
		'main_left' : ['category_thumb', ],
		'main_right' : ['image_widget', ],
		'sidebar' : ['contact_link', 'special_feature', 'page', 'link', ],
		'meta' : {'option_name': 'Photography (Root)'},
	},
	
	'page_root' : {
		'main_left' : ['page', 'page_widget', ],
		'main_right' : ['category', ],
		'sidebar' : ['contact_link', 'special_feature', 'link', ],
		'meta' : {'option_name': 'Writing (Root)'},
	},
	
	'code_root' : {
		'main_left' : ['page_widget', ],
		'main_right' : ['category', ],
		'sidebar' : ['contact_link', 'special_feature', 'page', 'link', ],
		'meta' : {'option_name': 'Code/Professional (Root)'},
	},
	
	'personal_root' : {
		'main_left' : 'desc',
		'main_right' : ['page', 'image', ],
		'sidebar' : ['category', 'contact_link', 'special_feature', 'link', 'upcoming_events', ],
		'meta' : {'option_name': 'Personal (Root)'},
	},
	
	'art_root' : {
		'main_left' : ['category_thumb', 'image', ],
		'main_right' : ['page', ],
		'sidebar' : ['contact_link', 'upcoming_events', 'special_feature', 'link', ],
		'meta' : {'option_name': 'Artwork (Root)'},
	},
	
	'char' : {
		'main' : 'desc',
		'main_2' : ['image', ],
		'sidebar' : ['contact_link', 'page', 'category', 'special_feature', 'link', ],
		'meta' : {'option_name': 'Character'},
	},
	
	'char_split' : {
		'main_left' : 'desc',
		'main_right' : ['image', ],
		'sidebar' : ['contact_link', 'page', 'category', 'special_feature', 'link', ],
		'meta' : {'option_name': 'Character (Split View)'},
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


#	deerbooks
#	Specify location of a working directory for compiling LaTeX source files.
DEERBOOKS_CACHE_DIR = os.path.abspath(os.path.join(BASE_DIR,'working_dirs/deerbooks/'))


#	sunset
#	Specify the maximum sizes, and other processing settings, for various image_asset types.
#	Size format is (width,height)
#	watermark=True means that assets of this type will be watermarked.
#	exact=True means that assets of this type will be fitted to these exact dimensions.
SUNSET_IMAGE_ASSET_SIZES = {
	'icon':{'size':(1500,250),'watermark':False,'exact':False,},
	'display':{'size':(1280,960),'watermark':True,'exact':False,},
	'full':{'size':(1920,1300),'watermark':True,'exact':False,},
	'bg':{'size':(1700,1000),'watermark':False,'exact':True,},
}
SUNSET_IMPORT_DIR = '/srv/awi_import/sunset'
SUNSET_CACHE_DIR = os.path.abspath(os.path.join(WORKING_DIR,'sunset/'))
SUNSET_WATERMARK_IMAGE = os.path.abspath(os.path.join(BASE_DIR,'sunset/watermarks/lupinia.png'))
SUNSET_BG_NOTIFY_FAIL = True	# Send a notification if sunset_bg is used but a background image cannot be found.


#	THIRD-PARTY APPS
#	==============
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


#	debug_toolbar
DEBUG_TOOLBAR_PATCH_SETTINGS = False


#	django_admin_tools
ADMIN_TOOLS_INDEX_DASHBOARD = 'awi.admin_tools_custom.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'awi.admin_tools_custom.CustomAppIndexDashboard'
ADMIN_TOOLS_MENU = 'awi.admin_tools_custom.CustomMenu'


#	s3_folder_storage
import boto.s3.connection
AWS_S3_CALLING_FORMAT = boto.s3.connection.OrdinaryCallingFormat()
AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False

DEFAULT_S3_PATH = 'awi'
STATIC_S3_PATH = 'awi-hagata'


#	django_processinfo
#	include app settings from ./django_processinfo/app_settings.py
from django_processinfo import app_settings as PROCESSINFO
PROCESSINFO.ADD_INFO = True
PROCESSINFO.INFO_SEARCH_STRING = '<span id="processinfo"></span>'
PROCESSINFO.INFO_FORMATTER = '<span id="processinfo">Render time:  %(total).1f ms</span>'

