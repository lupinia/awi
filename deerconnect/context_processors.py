#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Context Processors
#	=================

from django.conf import settings
from django.core.cache import cache

from deerconnect.models import contact_link
from awi_access.models import access_query

def social_icons(request):
	social_links = cache.get('social_links_%d' % settings.SITE_ID)
	if social_links is None:
		social_links = contact_link.objects.filter(featured=True).filter(access_query()).order_by('label')
		cache.set('social_links_%d' % settings.SITE_ID, social_links, 60*60*24)
	
	if social_links:
		return {'header_icons':social_links}
	else:
		return {'header_icons':False}
