#	Dagasi - Content Security (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions
#	=================

from dagasi.types import status

def default_userprefs():
	"""Default user preferences"""
	prefs = {
		'show_mature': status(False, 'access_mature_prompt'),
		'show_hidden': False,
		'view_cross_site': False,
	}
	return prefs
