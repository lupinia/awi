#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404

from awi_access.models import access_query
from awi_utils.views import json_response
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
			context['meta'] = context['object'].meta.filter(key__public=True).select_related('key')
			context['assets'] = {}
			asset_list = context['object'].assets.all()
			for asset in asset_list:
				context['assets'][asset.type] = asset
			
			if context['object'].geo_lat and context['object'].geo_long:
				# Setting up the map.
				context['map_type'] = 'photo_sub_map'
				context['map_tiles'] = 'outdoors'
				context['map_lat'] = context['object'].geo_lat
				context['map_long'] = context['object'].geo_long
			
			context['showcase_mode'] = True
			context['extra_classes'] = 'photo_page'
			
			if context['assets'].get('display', False):
				context['extra_style'] = 'max-width:%dpx;' % context['assets'].get('display', False).img_width
			
			if not context['object'].body:
				context['title_in_sidebar'] = True
			
			if context['can_edit']:
				context['edit_url'] = 'admin:sunset_image_change'
		else:
			context['image'] = ''
		
		return context


def geojson_image(request, slug, **kwargs):
	from deertrees.models import category, tag
	
	return_data = []
	query = image.objects.filter(access_query(request)).exclude(rebuild_assets=True, is_new=True).exclude(Q(geo_lat__isnull=True) | Q(geo_long__isnull=True)).order_by('-timestamp_post').select_related('cat').prefetch_related('assets')
	
	if slug == 'full_list':
		pass
	elif 'filter_cat' in slug:
		filter = slug.replace('filter_cat_','')
		filter_obj = get_object_or_404(category, slug=filter)
		query = query.filter(cat=filter_obj)
	elif 'filter_tag' in slug:
		filter = slug.replace('filter_tag_','')
		filter_obj = get_object_or_404(tag, slug=filter)
		query = query.filter(tag=filter_obj)
	elif slug == 'filter_featured':
		query = query.exclude(featured=False)
	else:
		request.session['deerfind_norecover'] = True
		raise Http404
	
	for item in query:
		if item.featured:
			marker_color = '#5b4aFF'
		elif item.mature:
			marker_color = '#c0283a'
		else:
			marker_color = '#5b4a71'
		
		#icon = item.assets.filter(type='icon').first()
		return_data.append({
			'type':'Feature',
			'geometry': {
				'type':'Point', 
				'coordinates':[item.geo_long, item.geo_lat],
			},
			'properties': {
				'marker-color':marker_color,
				'marker-size':'small', 
				'title':unicode(item),
				'description':unicode(item),
			},
		})
	
	return json_response(request, data=return_data)


# Helper functions for inclusion in other views.
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

def import_folder_widget(parent=False, parent_type=False, request=False):
	if parent and request and request.user and request.user.is_superuser and parent_type == 'category':
		queryset = batch_import.objects.filter(cat=parent).select_related()
		if queryset:
			return queryset
		else:
			return False
	
	else:
		return False


def finder(request):
	import os
	return_data = (False,'')
	
	basename = os.path.basename(request.path)
	if '.' in basename:
		search_slug_list = basename.split('.')
		search_slug = search_slug_list[0]
		
		image_check = image.objects.filter(slug__iexact=search_slug).filter(access_query(request)).select_related().first()
		if image_check:
			# Yay!  We found a match!  And it's authorized for viewing.
			return_data = (True, reverse('image_single', kwargs={'cached_url':image_check.cat.cached_url, 'slug':image_check.slug,}))
	
	return return_data
