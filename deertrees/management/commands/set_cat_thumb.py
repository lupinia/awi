#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Management Command:  set_cat_thumb
#	Sets a thumbnail for all categories that need one.
#	=================

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from awi_access.models import access_query
from deertrees.models import category
from sunset.models import image

class Command(BaseCommand):
	help = "Sets a thumbnail for all categories that need one."
	
	def handle(self, *args, **options):
		try:
			parents = category.objects.filter(view_type__in=['photo_root','art_root','image_split'])
			
			for parent in parents:
				child_cats = parent.children.all().order_by('title')
				child_imgs = image.objects.filter(cat__in=parent.get_descendants(include_self=True), published=True, assets__type='icon').filter(access_query()).order_by('-featured','-timestamp_post').prefetch_related('assets')
				if child_cats:
					return_data = []
					for cat in child_cats:
						if cat.icon_manual and cat.icon:
							self.stdout.write('Icon was manually overridden for category %s (%d).' % (cat, cat.pk))
						else:
							img_list = child_imgs.filter(cat__in=cat.get_descendants(include_self=True))
							thumb_img = False
							if img_list:
								img = img_list.first()
								thumb_img = img.assets.get(type='icon')
								cat.icon=thumb_img
								cat.icon_manual=False
								cat.save()
								self.stdout.write('Icon set to %s (%d) for category %s (%d).' % (img, img.pk, cat, cat.pk))
		
		except:
			import sys,traceback
			raise CommandError(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
