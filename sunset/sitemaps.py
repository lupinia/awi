#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Sitemap Objects
#	=================

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.db.models import Count

from awi_access.models import access_query
from sunset.models import image, background_tag

class image_map(Sitemap):
	priority = 0.8
	changefreq = 'weekly'
	
	def items(self):
		return image.objects.filter(access_query()).select_related('cat')
	
	def lastmod(self, obj):
		return obj.timestamp_mod

def html_map(request):
	"""Build a tree of relevant directories for this module based on the current request"""
	title_prefix = "Image Collection"
	root_dir = reverse('sunset_bgtags_all')
	dirtree = {}
	
	# Start with root, which will replace the special feature object
	dirtree['url'] = root_dir
	dirtree['title'] = 'Background Image Collections'
	dirtree['mode'] = 'path'
	dirtree['children'] = []
	
	child_list = background_tag.objects.all().annotate(num_leaves=Count('images')).order_by('tag')
	for instance in child_list:
		if instance.num_leaves:
			dirtree['children'].append(
				{
					'url': instance.get_absolute_url(),
					'title': '%s: %s' % (title_prefix, instance.title),
					'mode': 'file',
					'num_leaves': instance.num_leaves,
				}
			)
	
	dirtree['num_leaves'] = len(dirtree['children'])
	
	# Put it all together in a way that can be easily added to other context
	return root_dir, dirtree
