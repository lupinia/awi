#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Frontend
#	Settings for templates and layout
#	=================

import os

from .files import BASE_DIR

# =================
#	Template Config
TEMPLATES = [{
	'BACKEND': 'django.template.backends.django.DjangoTemplates',
	'DIRS' : [
		os.path.abspath(os.path.join(BASE_DIR,'./templates/showcase')),	# Per-theme directory
		os.path.abspath(os.path.join(BASE_DIR,'./templates/global')),	# Templates for all themes
	],
	'OPTIONS' : {
		'context_processors' : [
			'awi.context_processors.core',
			
			'django.contrib.auth.context_processors.auth',
			'django.template.context_processors.debug',
			'django.template.context_processors.i18n',
			'django.template.context_processors.tz',
			'django.contrib.messages.context_processors.messages',
			
			#	Non-standard ones
			'awi.context_processors.site',
			'awi.context_processors.meta',
			'deerconnect.context_processors.social_icons',
		],
		'loaders' : [
			#	It's really stupid that I have to add a custom template loader for django-admin-tools.
			#	Might be looking for a new alternative.
			'django.template.loaders.filesystem.Loader',
			'django.template.loaders.app_directories.Loader',
			
			'admin_tools.template_loaders.Loader',
		],
		'builtins' : [
			'django.templatetags.static',
			'sunset.templatetags.sunset_bg',
		],
	},
},]


# =================
#	DeerSky
#	Maximum number of secondary clocks on a homepage
#	When changing this, make sure the CSS supports all secondary clocks!
HOMEPAGE_MAX_EXTRA_CLOCKS = 12


# =================
#	DeerTrees
#	This stores a list of known models that can be attached to a category,
#	their hierarchy when displayed, and a template file's path
#	Model Name {
#		title: Displayable title, OR an image URL relative to {{STATIC_PREFIX}}, OR False,
#		template: Path to importable template,
#		is_leaf: Boolean; if False, this entry is data for a block that isn't a leaf,
#			but still has a foreign key to categories or tags, 
#		custom_obj: String; import path for a function that will be used for this block.
#			Use this for more complex queries, or content that doesn't
#			have a foreign key to a category or tag, 
#		count: Integer; number of leaves per page to display for this leaf type.
#			Zero == unlimited
#		prefetch: List; if present, this adds fields to prefetch_related,
#		related: List; if present, this adds fields to select_related,
DEERTREES_BLOCKS = {
	'image' : {
		'title':'Photography/Artwork',
		'template':'sunset/leaf_image.html',
		'is_leaf':True,
		'count':100,
		'prefetch':['assets',]
	},
	'page': {
		'title':'Writing',
		'template':'deerbooks/leaf_page.html',
		'is_leaf':True,
		'count':50,
		'related':['book_title',]
	},
	'link': {
		'title':'Links',
		'template':'deerconnect/leaf_link.html',
		'is_leaf':True,
		'count':0,
	},
	'special_feature': {
		'title':'Special Features',
		'template':'deertrees/leaf_feature.html',
		'is_leaf':True,
		'count':0,
	},
}

DEERTREES_BLOCKS_SPECIAL = {
	'category': {
		'title':'Subcategories',
		'template':'deertrees/leaf_subcat.html',
		'is_leaf':False,
		'custom_obj':'deertrees.views.subcats',
	},
	'contact_link': {
		'title':'Contact Natasha',
		'template':'deerconnect/leaf_contact_link.html',
		'is_leaf':False,
		'custom_obj':'deerconnect.views.contact_widget',
	},
	'category_thumb': {
		'title':'Subcategories',
		'template':'deertrees/leaf_subcats_thumb.html',
		'is_leaf':False,
		'custom_obj':'deertrees.views.subcats',
	},
	'upcoming_events': {
		'title':'Upcoming Events',
		'template':'deerattend/widget.html',
		'is_leaf':False,
		'custom_obj':'deerattend.views.widget',
	},
	'image_widget' : {
		'template':'sunset/image_widget.html',
		'is_leaf':True,
		'custom_obj':'sunset.views.recent_widget',
	},
	'image_folder_widget' : {
		'template':'sunset/folder_widget.html',
		'is_leaf':False,
		'custom_obj':'sunset.views.import_folder_widget',
	},
	'page_widget' : {
		'template':'deerbooks/page_widget.html',
		'is_leaf':True,
		'custom_obj':'deerbooks.views.recent_widget',
	},
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
