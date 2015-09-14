#	Lupinia Studios
#	By Natasha Long
#	www.lupinia.net - natasha@lupinia.net
#	
#	=================
#	Django Settings File
#	App-Specific Config
#
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
	'width': '100%',
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