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
	return {'site':Site.objects.get_current()}

def debug_check(request):
	return {'debug_check':settings.DEBUG}