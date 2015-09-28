#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Context Processors
#	=================

from django.contrib.sites.models import Site

from deerconnect.models import contact_link
from awi_access.models import access_query

def social_icons(request):
	social_links = contact_link.objects.filter(featured=True).filter(access_query(request)).order_by('label')
	if social_links:
		return {'header_icons':social_links}
	else:
		return {'header_icons':False}
