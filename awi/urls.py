from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.conf import settings

from awi_error.views import system_error
from deerfind.views import not_found

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
	
	#	My Apps
	url(r'^gamescripts/', include('secondlife.urls')),
	
	#	DeerTrees is a special case for my site, since it can be any directory or URL not otherwise specified.
	#url(r'^(?P<cached_url>[\w\d_/-]+)/$',structure_views.category_list.as_view(),name='category'),
)

if settings.DEBUG:
	import debug_toolbar
	urlpatterns += patterns('',url(r'^__debug__/', include(debug_toolbar.urls)),)

handler404=not_found
handler500=system_error
