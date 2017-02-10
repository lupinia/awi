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
	
	url(r'^event/(?P<slug>.*)/$', views.event_instances.as_view(), name='filter_event'),
	url(r'^venue/(?P<slug>.*)/$', views.events_by_venue.as_view(), name='filter_venue'),
	
	url(r'^flagged/(?P<slug>.*)/$', views.events_by_flag.as_view(), name='filter_flag'),
	url(r'^type/(?P<slug>.*)/$', views.events_by_type.as_view(), name='filter_type'),
	url(r'^filter/(?P<slug>.*)/$', views.events_by_special.as_view(), name='filter_special'),
	
	# Hackable URLs are a virtue.
	url(r'^event/$', views.full_list.as_view()),
	url(r'^venue/$', views.full_list.as_view()),
	url(r'^flagged/$', views.full_list.as_view()),
	url(r'^type/$', views.full_list.as_view()),
	url(r'^filter/$', views.full_list.as_view()),
]