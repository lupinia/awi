#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Search
#	Settings for Haystack and search config
#	=================

# =================
#	Haystack
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 50


# =================
#	DeerFind

#	Stores a dictionary of paths for search result templates for each indexed object.
#	Use the content type as the dictionary key.
SEARCH_RESULT_DATA = {
	# DeerAttend
	'deerattend.event_instance': {
		'display_name': 'Event',
		'default_icon':'event',
	},
	'deerattend.venue': {
		'display_name': 'Event Venue',
		'default_icon':'place',
	},
	
	# DeerBooks
	'deerbooks.page': {
		'display_name': 'Writing',
		'default_icon':'book',
		'template': 'deerbooks/content_thumb_page.html',
	},
	
	# DeerCoins
	'deercoins.coin': {
		'display_name': 'Coin Collection',
		'default_icon':'coin',
	},
	
	# DeerConnect
	'deerconnect.contact_link': {
		'display_name': 'Contact Link',
		'default_icon':'contact',
	},
	'deerconnect.link': {
		'display_name': 'External Link',
		'default_icon':'link',
	},
	
	# DeerFood
	'deerfood.menu_item': {
		'display_name': 'Kitchen Menu',
		'default_icon':'deerfood',
	},
	
	# DeerTrees
	'deertrees.category': {
		'display_name': 'Category',
		'default_icon':'category-misc',
		'template': 'deertrees/content_thumb_deertrees.html',
	},
	'deertrees.tag': {
		'display_name': 'Tag',
		'default_icon':'tag',
		'template': 'deertrees/content_thumb_deertrees.html',
	},
	
	# Sunset
	'sunset.image': {
		'display_name': 'Image',
		'default_icon':'image',
		'template': 'sunset/content_thumb_image.html',
	},
}

#	Fallback when a template isn't specified in SEARCH_RESULT_DATA
SEARCH_RESULT_TEMPLATE_DEFAULT = 'includes/content_thumb_default.html'

#	Default fields used for main/simple search form.
DEERFIND_DEFAULT_SEARCH_FIELDS = [
	'title',
	'text',
	'tags',
	'summary',
]
