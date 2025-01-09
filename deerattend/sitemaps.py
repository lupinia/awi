#	DeerAttend (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Sitemap Objects
#	=================

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from deerattend.models import attendance_flag, event, event_type, venue
from deerattend.views import special_filter_list

class event_type_map(Sitemap):
	priority = 0.4
	changefreq = 'yearly'
	
	def items(self):
		return event_type.objects.all()
	
	def lastmod(self, obj):
		return obj.timestamp_mod

class event_flag_map(Sitemap):
	priority = 0.4
	changefreq = 'yearly'
	
	def items(self):
		return attendance_flag.objects.all()
	
	def lastmod(self, obj):
		return obj.timestamp_mod

class event_special_filter_map(Sitemap):
	priority = 0.5
	changefreq = 'never'
	
	def items(self):
		return special_filter_list.keys()
	
	def location(self, item):
		return reverse('deerattend:filter_special', kwargs={'slug':item,})

class event_venue_map(Sitemap):
	priority = 0.3
	changefreq = 'yearly'
	
	def items(self):
		return venue.objects.all()
	
	def lastmod(self, obj):
		return obj.timestamp_mod

class event_map(Sitemap):
	priority = 0.5
	changefreq = 'yearly'
	
	def items(self):
		return event.objects.all()
	
	def lastmod(self, obj):
		return obj.timestamp_mod
