#	secondlife (Legacy Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL Map
#	=================

from django.conf.urls import include, url
from secondlife import views

urlpatterns = [
	url(r'^security_sl',views.security_response, {'system':'lupinia-old', 'zone':'LMC'} ,name='sl_security'),
	url(r'^security_oslup',views.security_response, {'system':'lupinia-os-old', 'zone':'LMC'} ,name='oslup_security'),
	url(r'^security_check.php',views.security_response, {'system':'lupinia-old', 'zone':'LMC'} ,name='legacy_sl_security'),
	url(r'^opensim_security_check.php',views.security_response, {'system':'lupinia-os-old', 'zone':'LMC'} ,name='legacy_oslup_security'),
]