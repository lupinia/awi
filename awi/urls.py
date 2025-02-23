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

from awi.utils.errors import system_error, request_error
from awi.sitemaps import SITEMAP_OBJECTS
from awi_access import views as access_views
from deerbooks import views as deerbooks_views
from deerconnect.views import contact_page
from deerfind.views import not_found, search_view, shortcode_redirect
from deersky.views import newtab_view
from deertrees import views as deertrees_views
from sunset import views as sunset_views

admin.autodiscover()
handler400 = request_error
handler404 = not_found
handler500 = system_error
handler403 = access_views.denied_error

urlpatterns = [
	# DeerFind: Shortcode redirect
	url(r'^s/(?P<type>.)(?P<pk>[0-9]+)', shortcode_redirect, name='shortcode'),
	
	# Django sitemap view
	url(r'^sitemap\.xml$', cache_control(max_age=60*60*48)(sitemap), {'sitemaps': SITEMAP_OBJECTS}, name='django.contrib.sitemaps.views.sitemap'),
	
	# Django admin views: Block without x509 cert
	url(r'^admin/', include(admin.site.urls)),
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin_tools/', include('admin_tools.urls')),
	
	# User authentication and management/settings
	url(r'^settings/$', access_views.settings_page.as_view(), name='settings'),
	url(r'^accounts/', include([
		url(r'^login/$', login_view, name='login'),
		url(r'^logout/$', logout_view, {'template_name':'registration/login.html'}, name='logout'),
		url(r'^age_form/$', never_cache(check_honeypot(field_name=settings.HONEYPOT_FIELD_NAME_AWIACCESS)(access_views.age_verify_full.as_view())), name='age_form'),
		url(r'^age_form_embed/$', never_cache(check_honeypot(field_name=settings.HONEYPOT_FIELD_NAME_AWIACCESS)(access_views.age_verify.as_view())), name='age_form_embed'),
	])),
	
	# DeerFind: Main search view
	url(r'^search/', search_view.as_view(), name='haystack_search'),
	
	# DeerConnect: Contact form
	url(r'^contact/$', never_cache(check_honeypot(contact_page.as_view())), name='contact'),
	
	# Sunset: Background image collections (bgtags)
	url(r'^backgrounds/$', sunset_views.bgtag_list.as_view(), name='sunset_bgtags_all'),
	url(r'^backgrounds/(?P<slug>.*)\.cfm$', sunset_views.img_bgtag_view.as_view(), name='sunset_bgtag'),
	
	# =====================================
	# DeerTrees: special_feature extension URLs
	# DeerFood
	url(r'^personal/cooking/menu/', include('deerfood.urls', namespace='deerfood'), kwargs={'special_feature_slug':'menu'}),
	
	# DeerAttend
	url(r'^furry/cons/', include('deerattend.urls',namespace='deerattend'), kwargs={'special_feature_slug':'cons'}),
	
	# DeerTrees sitemap view
	url(r'^about/sitemap\.htm$', cache_control(max_age=60*60*48)(deertrees_views.sitemap.as_view()), name='sitemap_htm', kwargs={'special_feature_slug':'sitemap.htm'}),
	
	# =====================================
	# /tools/ - Special subdirectory for utility views
	url(r'^tools/', include([
		# DeerTrees: Full category list
		url(r'^category_list\.ashx$', permission_required('deertrees.change_leaf')(deertrees_views.all_cats.as_view()), name='all_cats'),
		
		# Sunset: GeoJSON API (deprecated)
		url(r'^sunset/(?P<slug>.*)\.json$', sunset_views.geojson_image, name='sunset_geojson'),
		
		# DeerBuild: Plate generator
		url(r'^plate_generator/', include('deerbuild.urls', namespace='deerbuild')),
		
		# DeerSky: Newtab page
		url(r'^newtab\.html$', never_cache(newtab_view.as_view()), name='newtab_page'),
	])),
	
	# =====================================
	# /tags/ - Special subdirectory for DeerTrees tag views
	url(r'^tags/$', deertrees_views.all_tags.as_view(), name='all_tags'),
	url(r'^tags/(?P<slug>.*)/', include([
		url(r'^$', deertrees_views.tag_list.as_view(), name='tag'),
		url(r'^feed\.rss$', cache_control(max_age=60*60*6)(deertrees_views.tag_rssfeed()), name='tag_rss'),
		
		# Sunset: Aggregate gallery views for tags
		url(r'^featured\-images\.cfm$', sunset_views.img_tag_view.as_view(), name='tag_images_featured', kwargs={'viewtype':'featured'}),
		url(r'^recent\-images\.cfm$', sunset_views.img_tag_view.as_view(), name='tag_images_recent', kwargs={'viewtype':'recent'}),
		
		# Sunset: Image RSS feeds
		url(r'^featured\-images\.rss$', cache_control(max_age=60*60*6)(sunset_views.img_tag_feed()), name='tag_rss_images_featured', kwargs={'viewtype':'featured'}),
		url(r'^recent\-images\.rss$', cache_control(max_age=60*60*6)(sunset_views.img_tag_feed()), name='tag_rss_images_recent', kwargs={'viewtype':'recent'}),
	])),
	
	# =====================================
	# DEERTREES FILESYSTEM EMULATION
	# Homepage/root views
	url(r'^$', deertrees_views.homepage.as_view(), name='home'),
	url(r'^feed\.rss$', cache_control(max_age=60*60*12)(deertrees_views.main_rssfeed()), name='home_rss'),
	
	# Directories and core structure
	url(r'^(?P<cached_url>[\w\d_/-]+)/', include([
		# DeerBooks: Book views
		url(r'^book\.(?P<slug>.*)\.tex$', deerbooks_views.book_tex.as_view(), name='book_tex'),
		url(r'^book\.(?P<slug>.*)\.md$', deerbooks_views.book_md.as_view(), name='book_md'),
		url(r'^book\.(?P<slug>.*)\.txt$', deerbooks_views.book_txt.as_view(), name='book_txt'),
		
		# DeerBooks: Page views
		url(r'^(?P<slug>.*)\.htm$', deerbooks_views.single_page_htm.as_view(), name='page_htm'),
		url(r'^(?P<slug>.*)\.txt$', deerbooks_views.single_page_txt.as_view(), name='page_txt'),
		url(r'^(?P<slug>.*)\.md$', deerbooks_views.single_page_md.as_view(), name='page_md'),
		url(r'^(?P<slug>.*)\.tex$', deerbooks_views.single_page_tex.as_view(), name='page_tex'),
		
		# Sunset: Image views
		url(r'^(?P<slug>.*)\.ihtm$', sunset_views.single_image.as_view(), name='image_single'),
		
		# Aggregate gallery views and feeds for directory (Sunset)
		url(r'^featured\-images\.cfm$', sunset_views.img_cat_view.as_view(), name='category_images_featured', kwargs={'viewtype':'featured'}),
		url(r'^recent\-images\.cfm$', sunset_views.img_cat_view.as_view(), name='category_images_recent', kwargs={'viewtype':'recent'}),
		url(r'^featured\-images\.rss$', cache_control(max_age=60*60*6)(sunset_views.img_cat_feed()), name='category_rss_images_featured', kwargs={'viewtype':'featured'}),
		url(r'^recent\-images\.rss$', cache_control(max_age=60*60*6)(sunset_views.img_cat_feed()), name='category_rss_images_recent', kwargs={'viewtype':'recent'}),
		
		# Directory root (DeerTrees)
		url(r'^feed\.rss$', cache_control(max_age=60*60*6)(deertrees_views.cat_rssfeed()), name='category_rss'),
		url(r'^$', deertrees_views.category_list.as_view(), name='category'),
	])),
]

#	django-debug-toolbar
#	This varies a bit from the documentation, because these need to come before any wildcard URL maps
if settings.DEBUG:
	import debug_toolbar
	
	urlpatterns_debug = [
		url(r'^__debug__/', include(debug_toolbar.urls)),
		url(r'^intentional500/', system_error, name='intentional500'),
		url(r'^intentional400/', request_error, name='intentional400'),
		url(r'^intentional404/', not_found, name='intentional404'),
		url(r'^intentional403/', access_views.denied_error, name='intentional403'),
	]
	urlpatterns = urlpatterns_debug + urlpatterns
