#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings - App-Specific Config
#	Config options for apps that aren't part of Django
#	=================
import os

#	Not an external setting, but it's used in this file, so it needs to be here.
DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#	CUSTOM APPS
#	==============
#	deertrees
#	This stores a list of known models that can be attached to a category, their hierarchy when displayed, and a template file's path
#	Model Name { 
#				title: Displayable title, OR an image URL relative to {{static}},
#				template: Path to importable template,
#				sidebar: Hierarchy for sidebar,
#				main: Hierarchy for main content area,
#				is_leaf: Boolean; if False, this entry is data for a block that isn't a leaf, 
#				prefetch: List; if present, this adds fields to prefetch_related,
#				related: List; if present, this adds fields to select_related, }
DEERTREES_BLOCKS = {
	'image' : {'title':'Photography/Artwork', 'template':'sunset/leaf_image.html', 'main':1, 'is_leaf':True, 'prefetch':['assets',]},
	'page': {'title':'Writing', 'template':'deerbooks/leaf_page.html', 'sidebar':4, 'main':2, 'is_leaf':True, 'related':['book_title',]},
	'link': {'title':'Links', 'template':'deerconnect/leaf_link.html', 'sidebar':5, 'main':4, 'is_leaf':True},
	'special_feature': {'title':'Special Features', 'template':'deertrees/leaf_feature.html', 'sidebar':3, 'is_leaf':True},
	
	'contact_link': {'title':'Contact Natasha', 'template':'deerconnect/leaf_contact_link.html', 'sidebar':2, 'is_leaf':False},
	'category': {'title':'Subcategories', 'template':'deertrees/leaf_subcat.html', 'sidebar':1, 'main':3, 'is_leaf':False},
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
SUNSET_CACHE_DIR = os.path.abspath(os.path.join(BASE_DIR,'working_dirs/sunset/'))
SUNSET_WATERMARK_IMAGE = os.path.abspath(os.path.join(BASE_DIR,'sunset/watermarks/lupinia.png'))
SUNSET_BG_NOTIFY_FAIL = True	# Send a notification if sunset_bg is used but a background image cannot be found.


#	THIRD-PARTY APPS
#	==============
#	static_precompiler
STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE = True
STATIC_PRECOMPILER_COMPILERS = ( ('static_precompiler.compilers.SCSS', {"executable": "/usr/local/bin/sassc", "compass_enabled": False}), )
STATIC_PRECOMPILER_ROOT = os.path.abspath(os.path.join(BASE_DIR,'devCSS/'))
STATIC_PRECOMPILER_OUTPUT_DIR = 'css'


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


#	django_summernote
def attachment_path(instance, filename):
	from os.path import join
	from django.utils.text import slugify
	name_pieces = filename.split('.')
	filename = "%s.%s" % (slugify(name_pieces[0]),name_pieces[1])
	return join('misc', filename)

SUMMERNOTE_CONFIG = {
	'iframe': False,
	'airMode': False,
	'width': '90%',
	'height': 600,
	
	'styleWithTags': True,
	'prettifyHtml': True,
	'empty': ('', ''),
	
	'attachment_upload_to': attachment_path,
	'attachment_require_authentication': True,
	'attachment_storage_class': DEFAULT_FILE_STORAGE,
	'attachment_filesize_limit': 10485760,
	
	'toolbar': [
		['view', ['fullscreen', 'codeview']],
		['font', ['bold', 'italic', 'underline', 'superscript', 'subscript','strikethrough', 'clear']],
		['insert', ['link', 'picture', 'video', 'hr']],
		['para', ['ul', 'ol', 'paragraph']],
		['table', ['table']],
		['color', ['color']],
		['help', ['help']],
	],
	
	'inplacewidget_external_css': (
		'//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css',
		'//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.min.css',
	),
	'inplacewidget_external_js': (
		'//code.jquery.com/jquery-1.9.1.min.js',
		'//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js',
	),
}
