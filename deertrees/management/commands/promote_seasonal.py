#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Management Command:  Automatically Promote Seasonal Content
#	
#	This is purely for the Lupinia Studios website, to promote seasonal photography categories.
#	The content isn't removed, this just cycles which categories are at the top of the list.
#	Might become a core feature of either Awi Access or DeerTrees in the future.
#	This is also a highly experimental feature, we'll see if I end up liking it.
#	
#	Also includes Sunset background tags
#	
#	Current Schedule:
#		/photo/autumn:		Sep 1 - Nov 30
#		/photo/winter:		Nov 1 - Feb 28
#		/photo/spring:		Feb 1 - May 31
#		/photo/summer:		May 1 - Aug 31
#		/photo/christmas:	Nov 1 - Dec 31
#	=================

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone

from deertrees.models import category
from sunset.models import background_tag

class Command(BaseCommand):
	# List of category slugs to feature and unfeature for each month.
	months = {
		1:{
			'feature':['winter',],
			'unfeature':['autumn','spring','summer','christmas',],
		},
		2:{
			'feature':['winter','spring'],
			'unfeature':['autumn','summer','christmas',],
		},
		3:{
			'feature':['spring',],
			'unfeature':['autumn','winter','summer','christmas',],
		},
		4:{
			'feature':['spring',],
			'unfeature':['autumn','winter','summer','christmas',],
		},
		5:{
			'feature':['spring','summer',],
			'unfeature':['autumn','winter','christmas',],
		},
		6:{
			'feature':['summer',],
			'unfeature':['autumn','winter','spring','christmas',],
		},
		7:{
			'feature':['summer',],
			'unfeature':['autumn','winter','spring','christmas',],
		},
		8:{
			'feature':['summer',],
			'unfeature':['autumn','winter','spring','christmas',],
		},
		9:{
			'feature':['autumn',],
			'unfeature':['summer','winter','spring','christmas',],
		},
		10:{
			'feature':['autumn',],
			'unfeature':['summer','winter','spring','christmas',],
		},
		11:{
			'feature':['autumn','winter','christmas',],
			'unfeature':['spring','summer',],
		},
		12:{
			'feature':['winter','christmas',],
			'unfeature':['autumn','spring','summer',],
		},
	}
	
	def handle(self, *args, **kwargs):
		cur_time = timezone.now()
		if self.months.get(cur_time.month, False):
			# Categories
			category.objects.filter(slug__in=self.months[cur_time.month]['unfeature']).update(featured=False)
			category.objects.filter(slug__in=self.months[cur_time.month]['feature']).update(featured=True)
			
			# Background tags
			background_tag.objects.filter(tag__in=self.months[cur_time.month]['unfeature']).update(default=False)
			background_tag.objects.filter(tag__in=self.months[cur_time.month]['feature']).update(default=True)
			
			self.stdout.write('Featured:  %s\nUnfeatured:  %s\n' % (', '.join(self.months[cur_time.month]['feature']), ', '.join(self.months[cur_time.month]['unfeature'])))
		
		else:
			self.stdout.write('Error:  No feature/unfeature list for current month (%d)' % cur_time.month)
