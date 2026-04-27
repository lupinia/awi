#	DeerAttend (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Sitemap Objects
#	=================

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.db.models import Count

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

def html_map(request):
	"""Build a tree of relevant directories for this module based on the current request"""
	title_prefix = 'Events Attended'
	root_dir = reverse('deerattend:full_list')
	dirtree = {}
	
	# Start with root, which will replace the special feature object
	dirtree['url'] = root_dir
	dirtree['title'] = '%s:  Full List' % title_prefix
	dirtree['mode'] = 'path'
	dirtree['children'] = []
	
	# First child tree: Events
	events_tree = {
		'url': '%sevent/' % root_dir,
		'title': '%s:  Event Details' % title_prefix,
		'mode': 'empty',
		'children': [],
	}
	
	child_list = event.objects.all()
	if not request.user.is_superuser and not request.user.is_staff:
		child_list = child_list.exclude(mature=True)
	child_list = child_list.annotate(num_leaves=Count('event_instance'))
	for instance in child_list:
		if instance.num_leaves:
			events_tree['children'].append(
				{
					'url': instance.get_absolute_url(),
					'title': 'Event: %s' % instance.name,
					'mode': 'path',
					'num_leaves': instance.num_leaves,
				}
			)
	
	events_tree['num_leaves'] = len(events_tree['children'])
	dirtree['children'].append(events_tree)
	
	# Second child tree: Venues
	venue_tree = {
		'url': '%svenue/' % root_dir,
		'title': '%s:  Event Venues' % title_prefix,
		'mode': 'empty',
		'children': [],
	}
	
	child_list = venue.objects.all()
	if not request.user.is_superuser and not request.user.is_staff:
		child_list = child_list.exclude(private=True)
	child_list = child_list.annotate(num_leaves=Count('events'))
	for instance in child_list:
		if instance.num_leaves:
			venue_tree['children'].append(
				{
					'url': instance.get_absolute_url(),
					'title': 'Event Venue: %s' % instance.name,
					'mode': 'path',
					'num_leaves': instance.num_leaves,
				}
			)
	
	venue_tree['num_leaves'] = len(venue_tree['children'])
	dirtree['children'].append(venue_tree)
	
	# Extras that don't get a full enumeration
	# Special filters
	dirtree['children'].append(
		{
			'url': '%sfilter/' % root_dir,
			'title': '%s:  Event Special Filters' % title_prefix,
			'mode': 'empty',
			'num_leaves': len(special_filter_list.keys()),
		}
	)
	
	# Flags
	dirtree['children'].append(
		{
			'url': '%sflagged/' % root_dir,
			'title': '%s:  Event Filter Flags' % title_prefix,
			'mode': 'empty',
			'num_leaves': attendance_flag.objects.count(),
		}
	)
	
	# Types
	dirtree['children'].append(
		{
			'url': '%stype/' % root_dir,
			'title': '%s:  Event Type Categories' % title_prefix,
			'mode': 'empty',
			'num_leaves': event_type.objects.count(),
		}
	)
	
	# Put it all together in a way that can be easily added to other context
	return root_dir, dirtree
