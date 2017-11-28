#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Custom context processors for entire project
#	=================

from django.conf import settings
from django.contrib.sites.models import Site

def site(request):
	if '.eu' in request.get_host():
		show_cookie_banner = True
	else:
		show_cookie_banner = False
	
	return {
		'site':Site.objects.get_current(), 
		'domain_name':request.get_host(), 
		'cookie_banner':show_cookie_banner,
	}

def settings_vars(request):
	return {
		'debug_check':settings.DEBUG,
		'mapbox_token':settings.MAPBOX_KEY,
	}
