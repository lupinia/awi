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
]