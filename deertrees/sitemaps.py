#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Sitemap Objects
#	=================

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from awi_access.models import access_query
from deertrees.models import *

class tag_map(Sitemap):
	priority = 0.2
	changefreq = 'monthly'
	
	def items(self):
		return tag.objects.filter(sitemap_include=True)
	
	def lastmod(self, obj):
		return obj.timestamp_mod

class cat_map(Sitemap):
	priority = 0.6
	changefreq = 'monthly'
	
	def items(self):
		return category.objects.filter(access_query()).filter(sitemap_include=True)
	
	def lastmod(self, obj):
		return obj.timestamp_mod

class special_map(Sitemap):
	priority = 0.5
	changefreq = 'monthly'
	
	def items(self):
		return special_feature.objects.filter(access_query()).select_related('cat')
	
	def lastmod(self, obj):
		return obj.timestamp_mod

class static_map(Sitemap):
	priority = 0.5
	changefreq = 'yearly'
	
	def items(self):
		return ['contact','all_tags','home','sitemap_htm', 'settings']
	
	def location(self, item):
		return reverse(item)
