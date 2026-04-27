#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Sitemap Objects
#	=================

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.db.models import Count

from deerfood.models import menu_section, menu_flag

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

def html_map(request):
	"""Build a tree of relevant directories for this module based on the current request"""
	title_prefix = "Recipe Book"
	root_dir = reverse('deerfood:full_menu')
	dirtree = {}
	
	# Start with root, which will replace the special feature object
	dirtree['url'] = root_dir
	dirtree['title'] = '%s:  Full Menu' % title_prefix
	dirtree['mode'] = 'path'
	dirtree['children'] = [
		{
			'url': '%sflagged/' % root_dir,
			'title': '%s:  Filter Flags' % title_prefix,
			'mode': 'empty',
			'num_leaves': menu_flag.objects.count(),
		}
	]
	
	# First child tree: Sections
	section_tree = {
		'url': '%ssection/' % root_dir,
		'title': '%s:  Categories' % title_prefix,
		'mode': 'empty',
		'children': [],
	}
	
	child_list = menu_section.objects.all().annotate(num_leaves=Count('menu_item'))
	for instance in child_list:
		if instance.num_leaves:
			section_tree['children'].append(
				{
					'url': instance.get_absolute_url(),
					'title': 'Recipe Category: %s' % instance.name,
					'mode': 'path',
					'num_leaves': instance.num_leaves,
				}
			)
	
	section_tree['num_leaves'] = len(section_tree['children'])
	dirtree['children'].append(section_tree)
	
	# Put it all together in a way that can be easily added to other context
	return root_dir, dirtree
