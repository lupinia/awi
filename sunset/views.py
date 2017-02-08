#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.core.urlresolvers import reverse

from awi_access.models import access_query
from deertrees.views import leaf_view
from sunset.models import *

class single_image(leaf_view):
	model=image
	template_name='sunset/image_single.html'
	
	def get_queryset(self, *args, **kwargs):
		return super(single_image, self).get_queryset(*args, **kwargs).prefetch_related('assets')
	
	def get_context_data(self, **kwargs):
		context=super(single_image,self).get_context_data(**kwargs)
		
		if context['object']:
			context['photo_page'] = True
			context['meta'] = context['object'].meta.filter(key__public=True).select_related('key')
			context['assets'] = {}
			asset_list = context['object'].assets.all()
			for asset in asset_list:
				context['assets'][asset.type] = asset
		else:
			context['image'] = ''
		
		return context


def recent_widget(parent=False, parent_type=False, request=False):
	return_data = {'recent': [], 'featured': []}
	if parent_type == 'category' and parent:
		return_data['recent'] = image.objects.filter(cat__in=parent.get_descendants(include_self=True), published=True).filter(access_query(request)).exclude(rebuild_assets=True, is_new=True, featured=True).order_by('-timestamp_post').select_related('cat').prefetch_related('assets')[:12]
		return_data['featured'] = image.objects.filter(cat__in=parent.get_descendants(include_self=True), published=True, featured=True).filter(access_query(request)).exclude(rebuild_assets=True, is_new=True).order_by('-timestamp_post').select_related('cat').prefetch_related('assets')[:6]
		return return_data
	elif parent_type == 'tag' and parent:
		return_data['recent'] = image.objects.filter(tags=parent, published=True).filter(access_query(request)).exclude(rebuild_assets=True, is_new=True, featured=True).order_by('-timestamp_post').select_related('cat').prefetch_related('assets')[:12]
		return_data['featured'] = image.objects.filter(tags=parent, published=True, featured=True).filter(access_query(request)).exclude(rebuild_assets=True, is_new=True).order_by('-timestamp_post').select_related('cat').prefetch_related('assets')[:6]
		return return_data
	else:
		return False


def finder(request):
	import os
	return_data = (False,'')
	
	basename=os.path.basename(request.path)
	if '.' in basename:
		search_slug_list = basename.split('.')
		search_slug = search_slug_list[0]
		search_type = search_slug_list[-1]
		
		image_check = image.objects.filter(slug=search_slug)
		if image_check.exists():
			# Yay!  We found a match!  Let's make sure we can actually view it, though.
			access_check = image_check[0].can_view(request)
			if access_check[0]:
				# Ok cool, had to check your credentials!  It's just standard procedure, you know how it is around here.
				return_data = (True,reverse('image_single',kwargs={'cached_url':image_check[0].cat.cached_url,'slug':image_check[0].slug}))
	
	return return_data
