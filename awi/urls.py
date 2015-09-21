#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL map for entire site
#	=================

from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.conf import settings

from awi_error.views import system_error
from deerfind.views import not_found
from deertrees import views as deertrees_views

admin.autodiscover()

urlpatterns = patterns('',
	#	System/Core
	url(r'^admin/', include(admin.site.urls)),
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^accounts/login/','django.contrib.auth.views.login'),
	url(r'^accounts/logout/','django.contrib.auth.views.logout',{'template_name':'registration/login.html'}),
	
	#	Contributed
	url(r'^admin_tools/', include('admin_tools.urls')),
	url(r'^summernote/', include('django_summernote.urls')),
	
	#	Custom Apps
	url(r'^gamescripts/', include('secondlife.urls')),
	
	#	DeerTrees is a special case for this site.
	url(r'^tags/(?P<slug>.*)/$',deertrees_views.tag_list.as_view(),name='tag'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/$',deertrees_views.category_list.as_view(),name='category'),
)

#	django-debug-toolbar
#	This varies a bit from the documentation, because these need to come before any wildcard URL maps
if settings.DEBUG:
	import debug_toolbar
	urlpatterns_debug = patterns('',url(r'^__debug__/', include(debug_toolbar.urls)),)
	urlpatterns = urlpatterns_debug + urlpatterns


#	Error handlers
handler404=not_found
handler500=system_error
