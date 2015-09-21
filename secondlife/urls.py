#	secondlife (Legacy Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL Map
#	=================

from django.conf.urls import patterns, include, url
from secondlife import views

urlpatterns = patterns('',
	url(r'^security_sl',views.security_response, {'gridname':'sl'} ,name='sl_security'),
	url(r'^security_oslup',views.security_response, {'gridname':'opensim_lup'} ,name='oslup_security'),
	url(r'^security_check.php',views.security_response, {'gridname':'sl'} ,name='legacy_sl_security'),
	url(r'^opensim_security_check.php',views.security_response, {'gridname':'opensim_lup'} ,name='legacy_oslup_security'),
)