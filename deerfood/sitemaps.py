#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Sitemap Objects
#	=================

from django.contrib.sitemaps import Sitemap

from awi_access.models import access_query
from deerfood.models import *

class menu_cat_map(Sitemap):
	priority = 0.5
	changefreq = 'monthly'
	
	def items(self):
		return menu_section.objects.all()
	
	def lastmod(self, obj):
		return obj.timestamp_mod

class menu_flag_map(Sitemap):
	priority = 0.5
	changefreq = 'monthly'
	
	def items(self):
		return menu_flag.objects.all()
	
	def lastmod(self, obj):
		return obj.timestamp_mod
