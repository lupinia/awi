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
	# Add an option to switch the background to all-white, for development purposes.
	# I can do this pretty easily using my browser's dev tools, but it'd be nice to have it built-in.
	bg_white = False
	if settings.DEBUG and request.GET.get('nobg',False):
		bg_white = True
	
	return {
		'debug_check':settings.DEBUG,
		'debug_white_bg':bg_white,
		'mapbox_token':settings.MAPBOX_KEY,
	}
