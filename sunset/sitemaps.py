#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Sitemap Objects
#	=================

from django.contrib.sitemaps import Sitemap

from awi_access.models import access_query
from sunset.models import *

class image_map(Sitemap):
	priority = 0.8
	changefreq = 'weekly'
	
	def items(self):
		return image.objects.filter(access_query()).select_related('cat')
	
	def lastmod(self, obj):
		return obj.timestamp_mod