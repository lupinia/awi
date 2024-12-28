#	DeerBuild - Virtual World Creator Tools (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL Map
#	=================

from django.conf.urls import url
from django.views.decorators.cache import never_cache

from deerbuild.views import plate_generator, plate_generator_list, plate_generator_root

urlpatterns = [
	url(r'^$', plate_generator_root.as_view(), name='plategen_root'),
	url(r'^(?P<group>.*)/$', plate_generator_list.as_view(), name='plategen_list'),
	url(r'^(?P<group>.*)/(?P<territory>[A-Z]{4})-(?P<code>[A-Z]{2})\.cgi$', never_cache(plate_generator.as_view()), name='plategen'),
]