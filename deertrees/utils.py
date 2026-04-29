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
