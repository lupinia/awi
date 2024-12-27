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
	"""
	Context processor to add various system settings as context variables.
	
	Values:
		debug_check:  Bool, value of settings.DEBUG
		debug_white_bg:  Bool, True if settings.DEBUG is True and ?nobg=1 in URL
		mapbox_token:  Value of settings.MAPBOX_KEY
		locale:  Value of settings.LANGUAGE_CODE
	"""
	bg_white = False
	if settings.DEBUG and request.GET.get('nobg',False):
		bg_white = True
	
	return {
		'debug_check':settings.DEBUG,
		'debug_white_bg':bg_white,
		'mapbox_token':settings.MAPBOX_KEY,
		'locale':settings.LANGUAGE_CODE,
	}

def meta(request):
	"""
	Context processor to set up the initial values of header meta tags. 
	These will usually be overridden by views, but sensible defaults help a lot. 
	
	Values:
		title_site:  Overall title for the whole site
		title_page:  Page-specific title, defaults to an empty string
		title_img:  Image filename component, just set to 'fr'
		sitemeta_author_name:  Default content author name
		sitemeta_twitter:  Default content author Twitter handle
		sitemeta_page_type:  Default OpenGraph content type
		sitemeta_is_image:  Boolean, set to True if this is primarily image content 
		sitemeta_desc:  Default page summary
	"""
	return {
		'title_site':settings.SITE_TITLE,
		'title_page':'',
		'title_img':settings.SITE_TITLE_IMG_CODE,
		'sitemeta_author_name':settings.DEFAULT_AUTHOR_NAME,
		'sitemeta_twitter':settings.DEFAULT_AUTHOR_TWITTER,
		'sitemeta_page_type':'website',
		'sitemeta_is_image':False,
		'sitemeta_desc':'',
	}
