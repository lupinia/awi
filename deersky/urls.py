#	DeerSky - Digital Almanac and Weather Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL Map
#	=================

from django.conf.urls import url
from django.views.decorators.cache import never_cache

from deersky.views import homepage_view, homepage_list

urlpatterns = [
	url(r'^$', homepage_list.as_view(), name='newtab_list'),
	url(r'^(?P<slug>.*)\.jsp$', never_cache(homepage_view.as_view()), name='newtab'),
]