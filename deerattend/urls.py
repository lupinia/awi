#	DeerAttend (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL Map
#	=================

from django.conf.urls import include, url
from deerattend import views

urlpatterns = [
	url(r'^$', views.full_list.as_view(), name='full_list'),
	url(r'^(?P<slug>.*)\.json', views.geojson_event_instance, name='geojson'),
	url(r'^flagged/(?P<slug>.*)/$', views.events_by_flag.as_view(), name='filter_flag'),
	url(r'^type/(?P<slug>.*)/$', views.events_by_type.as_view(), name='filter_type'),
	url(r'^filter/(?P<slug>.*)/$', views.events_by_special.as_view(), name='filter_special'),
]