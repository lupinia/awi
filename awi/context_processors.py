#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Custom context processors for entire project
#	=================

import os

from django.conf import settings
from django.contrib.sites.models import Site

def site(request):
	"""
	Context processor to add values related to the current site and request.
	
	Values:
		site:  The entire current django.contrib.sites.Site object
		cookie_banner:  Boolean, True if the current domain is European
		ssl:  Boolean, True if this is an SSL connection
		domain_name:  Just the current domain name
		site_root:  Current domain name plus scheme, with a trailing slash
		permalink:  Full URL to the current page, minus any query arguments
		cwd:  Current Working Directory, minus any filename, with leading and trailing slashes
		cwd_absolute:  CWD plus domain and scheme, to reference files in the same directory
	"""
	
	site_data = {'site':Site.objects.get_current(), 'cookie_banner':False, 'ssl':False, 'certauth':False,}
	
	site_data['domain_name'] = request.get_host()
	if '.eu' in site_data['domain_name']:
		site_data['cookie_banner'] = True
	
	if request.scheme.lower() == 'https':
		site_data['ssl'] = True
	
	if request.META.get('HTTP_X_SSL_CLIENT_VERIFY','NONE') == 'SUCCESS':
		site_data['certauth'] = True
	
	site_data['site_root'] = '%s://%s/' % (request.scheme, site_data['domain_name'])
	site_data['permalink'] = '%s://%s%s' % (request.scheme, site_data['domain_name'], request.path)
	
	site_data['cwd'] = request.get_full_path()
	
	if '?' in site_data['cwd']:
		site_data['cwd'], discard = site_data['cwd'].split('?', 1)
	
	if os.path.basename(site_data['cwd']):
		# We need to parse out a directory from this
		if '.' in os.path.basename(site_data['cwd']):
			# This has a filename, so we want its parent directory
			site_data['cwd'] = os.path.dirname(site_data['cwd'])
		
		# Append a trailing slash to fix it
		site_data['cwd'] = '%s/' % site_data['cwd']
	
	site_data['cwd_absolute'] = '%s://%s%s' % (request.scheme, site_data['domain_name'], site_data['cwd'])
	
	return site_data

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
