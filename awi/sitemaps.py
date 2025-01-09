#	Django sitemap framework
#	Moved this here to clean up the URL config.
from deerattend.sitemaps import event_map, event_type_map, event_flag_map, event_special_filter_map, event_venue_map
from deerbooks.sitemaps import page_map
from deerfood.sitemaps import menu_cat_map, menu_flag_map
from deertrees.sitemaps import cat_map, tag_map, special_map, static_map
from sunset.sitemaps import image_map

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
