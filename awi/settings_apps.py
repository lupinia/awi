#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings - App-Specific Config
#	Config options for apps that aren't part of Django
#	=================

#	Not an external setting, but it's used in this file, so it needs to be here.
DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'


#	debug_toolbar
DEBUG_TOOLBAR_PATCH_SETTINGS = False


#	django_admin_tools
ADMIN_TOOLS_INDEX_DASHBOARD = 'awi.admin_dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'awi.admin_dashboard.CustomAppIndexDashboard'
ADMIN_TOOLS_MENU = 'awi.admin_menu.CustomMenu'


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
PROCESSINFO.INFO_FORMATTER = '<span id="processinfo">Render time:  %(total).1f ms &bull; Processinfo Module:  %(own).1f ms, %(perc).1f%% of total</span>'



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


#	deertrees
#	This stores a list of known models that can be attached to a category, their hierarchy when displayed, and a template file's path
#	Model Name { 
#				title: Displayable title, OR an image URL relative to {{static}},
#				template: Path to importable template,
#				sidebar: Hierarchy for sidebar,
#				main: Hierarchy for main content area, }
DEERTREES_BLOCKS = {
	'page': {'title':'Writing', 'template':'deerbooks/leaf_page.html', 'sidebar':3, 'main':1},
	'special_feature': {'title':'Special Features', 'template':'deertrees/leaf_feature.html', 'sidebar':1},
	'category': {'title':'Subcategories', 'template':'deertrees/leaf_subcat.html', 'sidebar':2, 'main':2},
}

#	Planned; roughly in order of content volume.
#DEERTREES_BLOCKS = {
#	'photo' : {'template':'sunset/catlistphoto_%(type).html', 'main':1}
#	'page' : {'template':'deerbooks/catlistpage_%(type).html', 'sidebar':4, 'main':3}
#	'menu_item' : {'template':'deerdine/menuitem_%(type).html', 'main':2}
#	'link' : {'template':'deerguide/link_%(type).html', 'sidebar':5}
#	'contact_link' : {'template':'deerguide/contactlink_%(type).html', 'sidebar':1}
#	'special_feature' : {'template':'deertrees/feature_%(type).html', 'sidebar':3}
#	'category' : {'template':'deertrees/childcat_%(type).html', 'sidebar':2, 'main':4}
#}