#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL Map
#	=================

from django.conf.urls import include, url
from deerfood import views

urlpatterns = [
	url(r'^$', views.full_menu.as_view(), name='full_menu'),
	url(r'^flagged/(?P<slug>.*)', views.menu_by_flag.as_view(), name='menu_flag'),
	url(r'^section/(?P<slug>.*)', views.menu_by_section.as_view(), name='menu_section'),
]