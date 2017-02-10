#	Django sitemap framework
#	Moved this here to clean up the URL config.
from deerattend.sitemaps import *
from deerbooks.sitemaps import *
from deerfood.sitemaps import *
from deertrees.sitemaps import *
from sunset.sitemaps import *

SITEMAP_OBJECTS = {
	'images':image_map,
	'writing':page_map,
	'directories':cat_map,
	'extras':special_map,
	
	'foodmenu':menu_cat_map,
	'foodflags':menu_flag_map,
	
	'eventtypes':event_type_map,
	'eventflags':event_flag_map,
	'eventspecial':event_special_filter_map,
	'eventvenues':event_venue_map,
	'events':event_map,
	
	'tags':tag_map,
	'static':static_map,
}
