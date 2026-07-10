#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL map additions for dev site
#	=================

from django.conf import settings
from django.conf.urls import include, url

from debug_toolbar import urls as debug_urls

from awi.urls import (
	handler400,
	handler403,
	handler404,
	handler500,
	urlpatterns,
)
from awi.utils.errors import system_error, request_error
from awi_access.views import denied_error
from deerfind.views import not_found

#	django-debug-toolbar
#	This varies a bit from the documentation, because these need to come before any wildcard URL maps
if settings.DEBUG:
	urlpatterns_debug = [
		url(r'^__debug__/', include(debug_urls)),
		url(r'^intentional500/', system_error, name='intentional500'),
		url(r'^intentional400/', request_error, name='intentional400'),
		url(r'^intentional404/', not_found, name='intentional404'),
		url(r'^intentional403/', denied_error, name='intentional403'),
	]
	urlpatterns = urlpatterns_debug + urlpatterns
