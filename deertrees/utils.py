#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions
#	=================

from django.conf import settings

def viewtype_options():
	blocks_map = settings.DEERTREES_BLOCK_MAP
	viewtypes = []
	for map_name, map in blocks_map.iteritems():
		if map.get('meta',{}).get('option_name',False) and map.get('meta',{}).get('selectable',True):
			viewtypes.append((map_name, map.get('meta',{}).get('option_name',map_name),))
	return viewtypes

def get_feeds(view_title, add_feeds=[], include_default=True):
	feed_list = []
	feed_source = []
	
	if include_default:
		feed_source += settings.DEERTREES_FEEDS.get('default', [])
	for feed_request in add_feeds:
		feed_source += settings.DEERTREES_FEEDS.get(feed_request, [])
	
	for feed in feed_source:
		if feed.get('title_override', False):
			feed['feed_title'] = feed['title_override']
		elif feed.get('title_suffix', False):
			feed['feed_title'] = '%s - %s' % (view_title, feed['title_suffix'])
		else:
			feed['feed_title'] = view_title
		
		feed_list.append(feed)
	
	return feed_list
