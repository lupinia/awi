#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Custom context processors for entire project
#	=================

from django.contrib.sites.models import Site

def site(request):
	return {'site':Site.objects.get_current()}