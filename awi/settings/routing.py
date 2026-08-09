#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Routing
#	Settings related to URL handling, redirects, and 404 recovery
#	=================

# Basic URL handling
APPEND_SLASH = True
ROOT_URLCONF = 'awi.urls'


# =================
#	Middleware Config
MIDDLEWARE = [
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'dagasi.middleware.UserPrefsMiddleware',
	'coreutils.sites.CurrentSiteMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =================
#	DeerFind

#	Stores a list of apps and their associated finder functions, in the event of a 404
#	If DeerFind can't match the URL to a known-bad one, it will check these until it gets a True, or runs out.
#	Finder functions should return a tuple; first value boolean (match found), second value a string (empty if no match, root-relative URL if match)
#	Can be on a per-app basis, not necessarily per-model
#	Ordering based on frequency of use is recommended, for increased efficiency
DEERFIND_FINDERS = [
	'deerfind.views.g2_finder',
	'deerbooks.views.finder',
	'deertrees.views.finder',
	'sunset.views.finder',
]

#	Shortcode model map
DEERFIND_SHORTCODE_TYPES = {
	'e': 'deerattend.event',
	'v': 'deerattend.venue',
	'p': 'deerbooks.page',
	'z': 'deersky.homepage',
	'c': 'deertrees.category',
	't': 'deertrees.tag',
	'x': 'deertrees.special_feature',
	'i': 'sunset.image',
}


# =================
#	DeerTrees
#	RSS feed sets
DEERTREES_FEEDS = {
	'default': [{'filename': 'feed.rss', 'title_suffix':'Newest Content (All)',},],
	'image': [
		{'filename': 'featured-images.rss', 'title_suffix':'Featured Images',},
		{'filename': 'recent-images.rss', 'title_suffix':'Newest Images',},
	],
}
