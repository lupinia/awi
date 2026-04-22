#	DeerSky - Digital Almanac and Weather Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL Map
#	=================

from django.conf.urls import url
from django.views.decorators.cache import never_cache

from deersky.views import newtab_view, homepage_view

urlpatterns = [
	url(r'^$', newtab_view.as_view(), name='newtab_default'),
	url(r'^(?P<slug>.*)\.jsp$', never_cache(homepage_view.as_view()), name='newtab'),
]