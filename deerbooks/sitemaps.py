#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Sitemap Objects
#	=================

from django.contrib.sitemaps import Sitemap

from awi_access.models import access_query
from deerbooks.models import *

class page_map(Sitemap):
	priority = 0.7
	changefreq = 'weekly'
	
	def items(self):
		return page.objects.filter(access_query()).select_related('cat')
	
	def lastmod(self, obj):
		return obj.timestamp_mod