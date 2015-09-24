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

from awi_error.views import system_error, denied_error
from deerfind.views import not_found
from deertrees import views as deertrees_views
from deerbooks import views as deerbooks_views

admin.autodiscover()
handler404 = not_found
handler500 = system_error
handler403 = denied_error

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
	
	#	DeerTrees and DeerBooks are special cases for this site.
	url(r'^$',deertrees_views.homepage.as_view(),name='home'),
	url(r'^tags/$',deertrees_views.all_tags.as_view(),name='all_tags'),
	url(r'^tags/(?P<slug>.*)/$',deertrees_views.tag_list.as_view(),name='tag'),
	
	url(r'^(?P<cached_url>[\w\d_/-]+)/(?P<slug>.*)\.htm',deerbooks_views.single_page_htm.as_view(),name='page_htm'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/(?P<slug>.*)\.txt',deerbooks_views.single_page_txt.as_view(),name='page_txt'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/(?P<slug>.*)\.md',deerbooks_views.single_page_md.as_view(),name='page_md'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/(?P<slug>.*)\.tex',deerbooks_views.single_page_tex.as_view(),name='page_tex'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/$',deertrees_views.category_list.as_view(),name='category'),
)

#	django-debug-toolbar
#	This varies a bit from the documentation, because these need to come before any wildcard URL maps
if settings.DEBUG:
	import debug_toolbar
	urlpatterns_debug = patterns('',
		url(r'^__debug__/', include(debug_toolbar.urls)),
		url(r'^intentional500/', system_error, name='intentional500'),
		url(r'^intentional404/', not_found, name='intentional404'),
		url(r'^intentional403/', denied_error, name='intentional403'),
	)
	urlpatterns = urlpatterns_debug + urlpatterns
