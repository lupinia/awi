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
	domain_name = request.get_host()
	if '.eu' in domain_name:
		show_cookie_banner = True
	else:
		show_cookie_banner = False
	
	return {
		'site':Site.objects.get_current(), 
		'domain_name':domain_name, 
		'cookie_banner':show_cookie_banner,
		'permalink':'%s://%s%s' % (request.scheme, domain_name, request.path),
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
		'locale':settings.LANGUAGE_CODE,
	}

def sitemeta(request):
	return {
		'title_site':settings.SITE_TITLE,
		'title_page':'',
		'title_img':settings.SITE_TITLE_IMG_CODE,
		'sitemeta_author_name':settings.DEFAULT_AUTHOR_NAME,
		'sitemeta_author_twitter':settings.DEFAULT_AUTHOR_TWITTER,
		'sitemeta_page_type':'website',
		'sitemeta_is_image':False,
		'sitemeta_desc':'',
	}
