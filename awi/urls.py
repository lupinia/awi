#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	URL map for entire site
#	=================

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import login as login_view
from django.contrib.auth.views import logout as logout_view
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.cache import cache_control, never_cache

from honeypot.decorators import check_honeypot

from awi.errors import system_error
from awi.sitemaps import SITEMAP_OBJECTS
from awi_access import views as access_views
from deerbooks import views as deerbooks_views
from deerconnect.views import contact_page
from deerfind.views import not_found, search_view, shortcode_redirect
from deersky.views import newtab_view
from deertrees import views as deertrees_views
from sunset import views as sunset_views

admin.autodiscover()
handler404 = not_found
handler500 = system_error
handler403 = access_views.denied_error

urlpatterns = [
	url(r'^s/(?P<type>.)(?P<pk>[0-9]+)', shortcode_redirect, name='shortcode'),
	
	url(r'^admin/', include(admin.site.urls)),
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin_tools/', include('admin_tools.urls')),
	
	url(r'^accounts/login/', login_view, name='login'),
	url(r'^accounts/logout/', logout_view, {'template_name':'registration/login.html'}, name='logout'),
	url(r'^accounts/age_form/$', never_cache(check_honeypot(field_name=settings.HONEYPOT_FIELD_NAME_AWIACCESS)(access_views.age_verify_full.as_view())), name='age_form'),
	url(r'^accounts/age_form_embed/$', never_cache(check_honeypot(field_name=settings.HONEYPOT_FIELD_NAME_AWIACCESS)(access_views.age_verify.as_view())), name='age_form_embed'),
	
	url(r'^settings/$', access_views.settings_page.as_view(), name='settings'),
	
	url(r'^search/', search_view.as_view(), name='haystack_search'),
	
	# APIs and utility views
	url(r'^tools/category_list/$', permission_required('deertrees.change_leaf')(deertrees_views.all_cats.as_view()), name='all_cats'),
	url(r'^tools/sunset/(?P<slug>.*)\.json', sunset_views.geojson_image, name='sunset_geojson'),
	url(r'^tools/plate_generator/', include('deerbuild.urls', namespace='deerbuild')),
	url(r'^tools/newtab\.html$', never_cache(newtab_view.as_view()), name='newtab_page'),
	
	# Special Features
	url(r'^contact/$', never_cache(check_honeypot(contact_page.as_view())), name='contact'),
	url(r'^personal/cooking/menu/', include('deerfood.urls', namespace='deerfood'), kwargs={'special_feature_slug':'menu'}),
	url(r'^furry/cons/', include('deerattend.urls',namespace='deerattend'), kwargs={'special_feature_slug':'cons'}),
	
	url(r'^sitemap\.xml$', sitemap, {'sitemaps': SITEMAP_OBJECTS}, name='django.contrib.sitemaps.views.sitemap'),
	
	# DeerTrees and DeerBooks are special cases for this site.
	url(r'^$', deertrees_views.homepage.as_view(), name='home'),
	url(r'^feed\.rss$', cache_control(max_age=60*60*12)(deertrees_views.main_rssfeed()), name='home_rss'),
	
	url(r'^tags/$', deertrees_views.all_tags.as_view(), name='all_tags'),
	url(r'^tags/(?P<slug>.*)/$', deertrees_views.tag_list.as_view(), name='tag'),
	url(r'^tags/(?P<slug>.*)/feed\.rss$', cache_control(max_age=60*60*6)(deertrees_views.tag_rssfeed()), name='tag_rss'),
	
	url(r'^about/sitemap\.htm$', cache_control(max_age=60*60*48)(deertrees_views.sitemap.as_view()), name='sitemap_htm', kwargs={'special_feature_slug':'sitemap.htm'}),
	
	url(r'^(?P<cached_url>[\w\d_/-]+)/book\.(?P<slug>.*)\.tex', deerbooks_views.book_tex.as_view(), name='book_tex'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/book\.(?P<slug>.*)\.md', deerbooks_views.book_md.as_view(), name='book_md'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/book\.(?P<slug>.*)\.txt', deerbooks_views.book_txt.as_view(), name='book_txt'),
	
	url(r'^(?P<cached_url>[\w\d_/-]+)/(?P<slug>.*)\.htm', deerbooks_views.single_page_htm.as_view(), name='page_htm'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/(?P<slug>.*)\.txt', deerbooks_views.single_page_txt.as_view(), name='page_txt'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/(?P<slug>.*)\.md', deerbooks_views.single_page_md.as_view(), name='page_md'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/(?P<slug>.*)\.tex', deerbooks_views.single_page_tex.as_view(), name='page_tex'),
	
	url(r'^(?P<cached_url>[\w\d_/-]+)/(?P<slug>.*)\.ihtm', sunset_views.single_image.as_view(), name='image_single'),
	
	url(r'^(?P<cached_url>[\w\d_/-]+)/feed\.rss$', cache_control(max_age=60*60*6)(deertrees_views.cat_rssfeed()), name='category_rss'),
	url(r'^(?P<cached_url>[\w\d_/-]+)/featured\-images\.cfm$', sunset_views.img_cat_view.as_view(), name='cat_images_featured', kwargs={'viewtype':'featured'}),
	url(r'^(?P<cached_url>[\w\d_/-]+)/recent\-images\.cfm$', sunset_views.img_cat_view.as_view(), name='cat_images_recent', kwargs={'viewtype':'recent'}),
	url(r'^(?P<cached_url>[\w\d_/-]+)/$', deertrees_views.category_list.as_view(), name='category'),
]

#	django-debug-toolbar
#	This varies a bit from the documentation, because these need to come before any wildcard URL maps
if settings.DEBUG:
	import debug_toolbar
	
	urlpatterns_debug = [
		url(r'^__debug__/', include(debug_toolbar.urls)),
		url(r'^intentional500/', system_error, name='intentional500'),
		url(r'^intentional404/', not_found, name='intentional404'),
		url(r'^intentional403/', access_views.denied_error, name='intentional403'),
	]
	urlpatterns = urlpatterns_debug + urlpatterns
