#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from awi.utils.views import json_response
from awi_access.models import access_query
from deerfind.utils import urlpath
from deertrees.models import category, tag
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
			context['sitemeta_desc'] = context['object'].summary_short
			context['sitemeta_is_image'] = True
			
			if context['assets'].get('display', False):
				context['extra_style'] = 'max-width:%dpx;' % context['assets'].get('display', False).img_width
			
			if not context['object'].long_body and not context['object'].public_domain:
				context['title_in_sidebar'] = True
			
			if context['object'].public_domain:
				context['public_domain_content'] = True
			
			if context['can_edit']:
				context['edit_url'] = 'admin:sunset_image_change'
			
		else:
			context['image'] = ''
		
		return context

# The purpose of this view is very similar to deertrees.views.category_list
# However, it doesn't need to be anywhere near as robust or functional
# And since it's specific to images, we're putting it here to keep things tidy 
class img_aggregate(object):
	model = image
	template_name = 'sunset/image_gallery.html'
	paginate_by = 50
	viewtype = 'recent'
	
	def view_title_base(self):
		if self.viewtype:
			return '%s Images' % self.viewtype.capitalize()
		else:
			return 'Images'
	
	def build_queryset(self, queryset=None, **kwargs):
		self.viewtype = kwargs.get('viewtype', 'recent')
		if queryset is None:
			queryset = image.objects
		
		if self.viewtype == 'featured':
			queryset = queryset.filter(featured=True).order_by('-timestamp_post')
		elif self.viewtype == 'recent':
			queryset = queryset.order_by('-timestamp_upload')
		
		return queryset.filter(access_query(getattr(self, 'request', False))).select_related('cat', 'access_code').prefetch_related('assets', 'tags')

class img_aggregate_cat(img_aggregate):
	slug_field = 'cached_url'
	slug_url_kwarg = 'cached_url'
	root = None
	
	def view_title(self):
		title = self.view_title_base()
		if self.root:
			title = u'%s - %s' % (unicode(self.root), title) # type: ignore
		return title
	
	def build_queryset(self, queryset=None, **kwargs):
		if kwargs.get(self.slug_url_kwarg, False):
			self.root = category.objects.filter(**{self.slug_field: kwargs[self.slug_url_kwarg],}).filter(access_query(getattr(self, 'request', False))).select_related('access_code').first()
			if self.root and self.root.can_view(getattr(self, 'request', False))[0]:
				catlist = self.root.get_descendants(include_self=True).filter(access_query(getattr(self, 'request', False))).select_related('access_code').values_list('pk', flat=True)
				return super(img_aggregate_cat, self).build_queryset(queryset, **kwargs).filter(cat__pk__in=catlist)
		
		return super(img_aggregate_cat, self).build_queryset(queryset, **kwargs).none()

class img_aggregate_tag(img_aggregate):
	slug_field = 'slug'
	slug_url_kwarg = 'slug'
	root = None
	
	def view_title(self):
		title = self.view_title_base()
		if self.root:
			title = u'%s - %s' % (unicode(self.root), title) # type: ignore
		return title
	
	def build_queryset(self, queryset=None, **kwargs):
		if kwargs.get(self.slug_url_kwarg, False):
			self.root = get_object_or_404(tag, **{self.slug_field: kwargs[self.slug_url_kwarg],})
			return super(img_aggregate_tag, self).build_queryset(queryset, **kwargs).filter(tags=self.root)
		else:
			return super(img_aggregate_tag, self).build_queryset(queryset, **kwargs).none()

class img_cat_view(img_aggregate_cat, ListView):
	def get_queryset(self):
		queryset = super(img_cat_view, self).get_queryset()
		queryset = self.build_queryset(queryset, **self.kwargs)
		if queryset.exists():
			return queryset
		else:
			raise Http404
	
	def get_context_data(self, **kwargs):
		context = super(img_cat_view, self).get_context_data(**kwargs)
		if not self.root:
			raise Http404
		
		canview, reason = self.root.can_view(self.request)
		if not canview:
			if reason == 'access_404':
				self.request.session['deerfind_norecover'] = True
				raise Http404
			else:
				raise PermissionDenied
		else:
			if self.viewtype == 'featured':
				context['highlight_featured'] = False
			else:
				context['highlight_featured'] = True
			
			context['title_view'] = self.view_title_base()
			context['category'] = self.root
			
			# Breadcrumbs
			ancestors = self.root.get_ancestors(include_self=True)
			if not context.get('breadcrumbs',False):
				context['breadcrumbs'] = []
			
			for crumb in ancestors:
				context['breadcrumbs'].append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
			
			context['breadcrumbs'].append({'url':reverse('category_images_%s' % self.viewtype, kwargs={'cached_url':self.root.cached_url,}), 'title':self.view_title_base()})
			
			# Metadata
			context['title_page'] = self.view_title()
		
		return context

class img_tag_view(img_aggregate_tag, ListView):
	def get_queryset(self):
		queryset = super(img_tag_view, self).get_queryset()
		queryset = self.build_queryset(queryset, **self.kwargs)
		if queryset.exists():
			return queryset
		else:
			raise Http404
	
	def get_context_data(self, **kwargs):
		context = super(img_tag_view, self).get_context_data(**kwargs)
		if not self.root:
			raise Http404
		
		canview, reason = self.root.can_view(self.request)
		if not canview:
			if reason == 'access_404':
				self.request.session['deerfind_norecover'] = True
			raise Http404
		else:
			if self.viewtype == 'featured':
				context['highlight_featured'] = False
			else:
				context['highlight_featured'] = True
			
			context['title_view'] = self.view_title_base()
			context['tag'] = self.root
			
			# Breadcrumbs
			if not context.get('breadcrumbs',False):
				context['breadcrumbs'] = []
			
			context['breadcrumbs'].append({'url':reverse('all_tags'), 'title':'Tags'})
			context['breadcrumbs'].append({'url':reverse('tag',kwargs={'slug':self.root.slug,}), 'title':unicode(self.root)}) # type: ignore
			context['breadcrumbs'].append({'url':reverse('tag_images_%s' % self.viewtype, kwargs={'slug':self.root.slug,}), 'title':self.view_title_base()})
			
			# Metadata
			context['title_page'] = self.view_title()
			
		return context

class img_all_view(img_aggregate, ListView):
	def get_queryset(self):
		queryset = super(img_all_view, self).get_queryset()
		queryset =  self.build_queryset(queryset, **self.kwargs)
		if queryset.exists():
			return queryset
		else:
			self.request.session['deerfind_norecover'] = True
			raise Http404

class img_aggregate_feed(Feed):
	author_name = "Natasha L."
	item_author_name = "Natasha L."
	description = "Photography, writing, and creative works by Natasha L."
	feed_copyright = timezone.now().strftime('Copyright (c) 2000-%Y Natasha L.')
	kwargs = {}
	
	def items(self, obj=None):
		if obj:
			return self.build_queryset(**self.kwargs)[:100]
		else:
			raise Http404
	
	def title(self):
		return self.view_title()
	
	def item_pubdate(self, item):
		return item.timestamp_upload
	
	def item_updateddate(self, item):
		return item.timestamp_mod
	
	def item_categories(self, item):
		return item.tags.all().values_list('slug', flat=True)
	
	def item_description(self, item):
		return item.rss_description
	
	def item_enclosure_url(self, item):
		enclosure_obj = getattr(item, 'rss_enclosure_obj', None)
		return getattr(enclosure_obj, 'rss_enclosure_url', None)
	
	def item_enclosure_length(self, item):
		enclosure_obj = getattr(item, 'rss_enclosure_obj', None)
		return getattr(enclosure_obj, 'rss_enclosure_length', None)
	
	def item_enclosure_mime_type(self, item):
		enclosure_obj = getattr(item, 'rss_enclosure_obj', None)
		return getattr(enclosure_obj, 'rss_enclosure_type', None)

class img_cat_feed(img_aggregate_cat, img_aggregate_feed):
	def get_object(self, request, **kwargs):
		self.kwargs = kwargs
		obj = get_object_or_404(category, cached_url=kwargs.get('cached_url',None))
		if obj.can_view(request)[0]:
			self.viewtype = kwargs.get('viewtype', 'recent')
			return obj
		else:
			request.session['deerfind_norecover'] = True
			raise Http404
	
	def link(self, obj=None):
		if obj:
			return reverse('category_images_%s' % self.viewtype, kwargs={'cached_url':obj.cached_url,})
		else:
			return "/"

class img_tag_feed(img_aggregate_tag, img_aggregate_feed):
	def get_object(self, request, **kwargs):
		self.kwargs = kwargs
		obj = get_object_or_404(tag, slug=kwargs.get('slug',None))
		if obj.can_view(request)[0]:
			self.viewtype = kwargs.get('viewtype', 'recent')
			return obj
		else:
			request.session['deerfind_norecover'] = True
			raise Http404
	
	def link(self, obj=None):
		if obj:
			return reverse('tag_images_%s' % self.viewtype, kwargs={'slug':obj.slug,})
		else:
			return "/"


def geojson_image(request, slug, **kwargs):
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
				'title':unicode(item), # type: ignore
				'description':unicode(item), # type: ignore
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
	is_found = False
	found_url = ''
	path = urlpath(request.path, force_lower=True)
	
	if path.is_file:
		# Only proceed if this path contains a filename
		image_check = image.objects.filter(basename__iexact=path.filename).select_related().first()
		if image_check:
			# Yay!  We found a match!  But can you view it?
			is_found = True
			perm_check, reason = image_check.can_view(request)
			if perm_check or reason == 'access_mature_prompt':
				# Yay!  We found a match that you're allowed to view!
				found_url = reverse('image_single', kwargs={'cached_url':image_check.cat.cached_url, 'slug':image_check.basename,})
	
	return (is_found, found_url)
