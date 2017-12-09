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
from sunset.models import image_asset

class Command(BaseCommand):
	help = "Sets a thumbnail for all categories that need one."
	
	def handle(self, *args, **options):
		try:
			cats = category.objects.all().exclude(trash=True).prefetch_related('leaves','sites')
			
			for cat in cats:
				# Step 1: Figuring out what type of folder this is.
				# Let's start by checking if we even need to do this, by checking whether anything has changed since the last run.
				if cat.leaves.filter(timestamp_mod__gt=cat.timestamp_mod).exists():
					# Ok, clearly we need to re-evaluate the contents of this folder
					# I feel like there should be a way to do this with a queryset, but I couldn't find a viable solution.
					# The idea here is to figure out which type of content this folder has the most of.
					# So, we want to get the leaf type that occurs with the greatest frequency.
					# If that leaf type is a known option, it will be the new content summary.
					# If that leaf type is not a known option (meaning we don't have an image for it), the content summary will be the default value.
					# Also, if there are more subcategories than leaves of the most common type, the content summary will be the default value.
					
					cat_contents = {}
					types_contained = cat.leaves.all().distinct('type').order_by('-type').values_list('type', flat=True)
					
					# The dictionary key is the count, to make it easier to sort them and grab the largest one
					if types_contained:
						for type_key in types_contained:
							type_count = cat.leaves.filter(type=type_key).count()
							cat_contents[type_count] = type_key
					
					# Check subcategories
					child_count = cat.get_children().count()
					
					# Putting it all together
					type_count_list = list(cat_contents.keys())
					type_count_list.sort()
					new_content_summary = 'misc'
					if type_count_list:
						if type_count_list[0] > child_count:
							new_content_summary = cat_contents.get(type_count_list[0], 'misc')
							cat.set_content_summary(new_content_summary)
							self.stdout.write('Content type summary set to %s for category %s (%d).' % (new_content_summary, cat, cat.pk))
				
				
				# Step 2:  Mapping an icon
				if not cat.icon_manual:
					# Trying the category's direct contents first
					asset_query = image_asset.objects.filter(parent__cat=cat, type='icon', parent__security__lte=cat.security, parent__published=True, parent__sites__pk__in=cat.sites.all().values_list('pk', flat=True)).order_by('-parent__featured','-parent__timestamp_post').select_related('parent')
					if not cat.mature:
						asset_query = asset_query.exclude(parent__mature=True)
					asset = asset_query.first()
					
					if asset and cat.icon != asset:
						cat.icon = asset
						cat.save()
						self.stdout.write('Icon set to %s (%d) for category %s (%d).' % (asset.parent, asset.parent.pk, cat, cat.pk))
					else:
						# No viable image directly contained in the current category.
						# We could check the descendant subcategories, but that would lead to pretty much every category site-wide having an image.
						# So, let's skip that for now, and see how the overall content looks.
						pass
		
		
		except:
			import sys,traceback
			raise CommandError(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
