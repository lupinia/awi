#	DeerAttend (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import generic

from awi_access.models import check_mature
from awi_utils.views import json_response
from deerattend.models import *
from deertrees.views import special_feature_view

special_filter_list = {
	'photos':{'name':'Events with Photos', 'slug':'photos', 'filter':Q(photos__isnull=False), 'is_mature':False, },
	'reports':{'name':'Events with Reports', 'slug':'reports', 'filter':Q(report__isnull=False), 'is_mature':False, },
	'upcoming':{'name':'Confirmed Upcoming Appearances', 'slug':'upcoming', 'filter':Q(confirmed=True) & Q(date_start__gte=timezone.now()), 'is_mature':False, },
	'tentative':{'name':'Tentative Upcoming Appearances', 'slug':'tentative', 'filter':Q(confirmed=False) & Q(date_start__gte=timezone.now()), 'is_mature':False, },
	'mature':{'name':'Mature (18+)', 'slug':'mature', 'filter':Q(event__mature=True), 'is_mature':True, },
	'no-mature':{'name':'Hide Mature', 'slug':'no-mature', 'filter':Q(event__mature=False), 'is_mature':True, },
}

# Base class for all of the other event list views
class event_list(special_feature_view, generic.ListView):
	model = event_instance
	context_object_name = 'event_instances'
	template_name = 'deerattend/event_list.html'
	mature_check = (None, '')
	
	geojson_slug = None
	special_filters = special_filter_list
	
	def get_mature_check(self):
		if self.mature_check[0] is None:
			self.mature_check = check_mature(self.request)
		return self.mature_check
	
	def filtered_queryset(self, *args, **kwargs):
		if self.request.user.is_superuser or self.request.user.is_staff:
			# Privileged User
			queryset = event_instance.objects.all()
		else:
			# Regular or anonymous user
			queryset = event_instance.objects.filter(Q(confirmed=True) | Q(date_start__gte=timezone.now()))
		
		if not self.get_mature_check()[0]:
			queryset = queryset.exclude(event__mature=True)
		
		return queryset.order_by('-date_start').prefetch_related('flags').select_related('event','event__type','venue','photos','report')
	
	def build_breadcrumbs(self, cur=False, cur_type=''):
		breadcrumbs = self.breadcrumbs()
		if breadcrumbs:
			if cur and cur_type:
				if cur_type == 'special':
					breadcrumbs.append({'url':reverse('deerattend:filter_'+cur_type, kwargs={'slug':cur['slug']}), 'title':cur['name']})
				else:
					breadcrumbs.append({'url':reverse('deerattend:filter_'+cur_type, kwargs={'slug':cur.slug}), 'title':cur.name})
			
			if self.request.GET.get('display', False) == 'map' and self.geojson_slug:
				breadcrumbs.append({'url':'?display=map', 'title':'Map View'})
			
			return breadcrumbs
		else:
			return False
	
	def can_edit(self):
		if self.request.user.is_authenticated():
			if self.request.user.has_perm('deertrees.change_event'):
				return True
			else:
				return False
		else:
			return False
	
	def get_filters(self):
		if self.request.user.is_superuser or self.request.user.is_staff:
			# Privileged User
			type_query = event_type.objects.all()
			flag_query = attendance_flag.objects.all()
		else:
			# Regular or anonymous user
			type_query = event_type.objects.filter(Q(event__event_instance__confirmed=True) | Q(event__event_instance__date_start__gte=timezone.now()))
			flag_query = attendance_flag.objects.filter(Q(event_instance__confirmed=True) | Q(event_instance__date_start__gte=timezone.now()))
		
		if not self.get_mature_check()[0]:
			type_query = type_query.exclude(event__mature=True)
			flag_query = flag_query.exclude(event_instance__event__mature=True)
		
		filters = {}
		filters['types'] = type_query.order_by('name').annotate(num_items=Count('event__event_instance'))
		filters['flags'] = flag_query.order_by('name').annotate(num_items=Count('event_instance'))
		filters['special'] = []
		for slug, special in self.special_filters.iteritems():
			if special.get('is_mature',False) and not self.get_mature_check()[0]:
				pass
			else:
				filters['special'].append(special)
		return filters
	
	def get_context_data(self, **kwargs):
		context = super(event_list, self).get_context_data(**kwargs)
		context['filters'] = self.get_filters()
		context['can_edit'] = self.can_edit()
		context['title_page'] = "Events Attended"
		
		if context['event_instances']:
			last_update = context['event_instances'].values('timestamp_mod').latest('timestamp_mod')
			context['update_time'] = last_update.get('timestamp_mod', False)
			
			photo_cat = context['event_instances'].exclude(photos__isnull=True).first()
			if photo_cat:
				context['category'] = photo_cat.photos
		else:
			context['error'] = 'filter_empty'
		
		context['geojson_slug'] = self.geojson_slug
		if self.request.GET.get('display', False) == 'map' and self.geojson_slug:
			self.template_name = 'deerattend/event_map.html'
			context['is_map_view'] = True
			context['map_type'] = 'fullpage_map'
			context['map_data_url'] = reverse('deerattend:geojson', kwargs={'slug':self.geojson_slug,})
			if context['error'] == 'filter_empty':
				context['error'] = None
		else:
			context['is_map_view'] = False
		
		return context



class full_list(event_list):
	def get_queryset(self, *args, **kwargs):
		if self.request.GET.get('display', False) == 'map':
			return event_instance.objects.none()
		else:
			return self.filtered_queryset(*args, **kwargs)
	
	def get_context_data(self, **kwargs):
		self.geojson_slug = 'full_list'
		
		context=super(full_list,self).get_context_data(**kwargs)
		context['breadcrumbs'] = self.build_breadcrumbs()
		return context


class event_instances(event_list):
	template_name = 'deerattend/event_detail.html'
	
	def get_queryset(self, *args, **kwargs):
		return self.filtered_queryset(*args, **kwargs).filter(event__slug=self.kwargs['slug'])
	
	def get_context_data(self, **kwargs):
		cur_filter = get_object_or_404(event, slug=self.kwargs['slug'])
		self.geojson_slug = 'event_%s' % cur_filter.slug
		
		context = super(event_instances,self).get_context_data(**kwargs)
		context['is_map_view'] = False
		context['cur_filter'] = cur_filter
		context['cur_filter_type'] = 'event'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'event')
		context['title_page'] = "%s - %s" % (context['title_page'], cur_filter.name)
		
		if cur_filter.mature and not self.get_mature_check()[0]:
			context['event_instances'] = []
			context['error'] = self.get_mature_check()[1]
			if self.get_mature_check()[1] == 'access_mature_prompt':
				context['embed_mature_form'] = True
				context['title_page'] += " (Mature Content)"
				context['sitemeta_desc'] = "Viewing this content requires verifying your age, which will not be stored on our server in any way.  More details on the form, or in our Privacy Policy."
		
		if context['event_instances']:
			venue_count = context['event_instances'].aggregate(Count('venue', distinct=True))
			if venue_count.get('venue__count', 0) > 1:
				context['geojson_slug'] = 'event_%s' % cur_filter.slug
				context['is_split_view'] = True
				context['map_type'] = 'events_sub_map'
				context['map_data_url'] = reverse('deerattend:geojson', kwargs={'slug':context['geojson_slug'],})
			else:
				single_location = context['event_instances'].first()
				context['single_location'] = '%s (%s)' % (unicode(single_location.venue), single_location.venue.get_city())
		
		return context


class events_by_type(event_list):
	def get_queryset(self, *args, **kwargs):
		if self.request.GET.get('display', False) == 'map':
			return event_instance.objects.none()
		else:
			return self.filtered_queryset(*args, **kwargs).filter(event__type__slug=self.kwargs['slug'])
	
	def get_context_data(self, **kwargs):
		cur_filter = get_object_or_404(event_type, slug=self.kwargs['slug'])
		self.geojson_slug = 'filter_type_%s' % cur_filter.slug
		
		context = super(events_by_type,self).get_context_data(**kwargs)
		context['cur_filter'] = cur_filter
		context['cur_filter_type'] = 'type'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'type')
		context['title_page'] = "%s - %s" % (context['title_page'], cur_filter.name)
		
		return context


class events_by_venue(event_list):
	def get_queryset(self, *args, **kwargs):
		return self.filtered_queryset(*args, **kwargs).filter(venue__slug=self.kwargs['slug'])
	
	def get_context_data(self, **kwargs):
		cur_filter = get_object_or_404(venue, slug=self.kwargs['slug'])
		
		context = super(events_by_venue,self).get_context_data(**kwargs)
		context['cur_filter'] = cur_filter
		context['cur_filter_type'] = 'venue'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'venue')
		context['title_page'] = "%s - %s" % (context['title_page'], cur_filter.name)
		
		return context


class events_by_flag(event_list):
	def get_queryset(self, *args, **kwargs):
		if self.request.GET.get('display', False) == 'map':
			return event_instance.objects.none()
		else:
			return self.filtered_queryset(*args, **kwargs).filter(flags__slug=self.kwargs['slug'])
	
	def get_context_data(self, **kwargs):
		cur_filter = get_object_or_404(attendance_flag, slug=self.kwargs['slug'])
		self.geojson_slug = 'filter_flag_%s' % cur_filter.slug
		
		context = super(events_by_flag,self).get_context_data(**kwargs)
		context['cur_filter'] = cur_filter
		context['cur_filter_type'] = 'flag'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'flag')
		context['title_page'] = "%s - %s" % (context['title_page'], cur_filter.name)
		return context


class events_by_special(event_list):
	def get_queryset(self, *args, **kwargs):
		if self.special_filters.get(self.kwargs['slug'], False):
			if self.special_filters[self.kwargs['slug']].get('is_mature', False) and not self.get_mature_check()[0]:
				return event_instance.objects.none()
			else:
				return self.filtered_queryset(*args, **kwargs).filter(self.special_filters[self.kwargs['slug']].get('filter', Q()))
		else:
			return self.filtered_queryset(*args, **kwargs)
	
	def get_context_data(self, **kwargs):
		context=super(events_by_special,self).get_context_data(**kwargs)
		context['cur_filter'] = self.special_filters.get(self.kwargs['slug'], False)
		context['cur_filter_type'] = 'special'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'special')
		context['title_page'] = "%s - %s" % (context['title_page'], context['cur_filter']['name'])
		
		if self.special_filters.get(self.kwargs['slug'], {}).get('is_mature', False) and not self.get_mature_check()[0]:
			context['event_instances'] = []
			context['error'] = self.get_mature_check()[1]
			if self.get_mature_check()[1] == 'access_mature_prompt':
				context['embed_mature_form'] = True
				context['title_page'] += " (Mature Content)"
				context['sitemeta_desc'] = "Viewing this content requires verifying your age, which will not be stored on our server in any way.  More details on the form, or in our Privacy Policy."
		
		if not context['event_instances'] and not context.get('error', False):
			context['error'] = 'filter_empty'
		
		return context


# Non-class-based views and helper objects.
def widget(parent=False, parent_type=False, request=False):
	queryset = event_instance.objects.filter(date_start__gte=timezone.now())
	if request:
		mature_check = check_mature(request)
		if not mature_check[0]:
			queryset = queryset.exclude(event__mature=True)
	else:
		queryset = queryset.exclude(event__mature=True)
	
	events_list = queryset.order_by('date_start').prefetch_related('flags').select_related('event','event__type','venue','photos','report')[:10]
	if events_list:
		return events_list
	else:
		return False



def geojson_event_instance(request, slug, **kwargs):
	return_data = []
	mature_check = check_mature(request)
	query = venue.objects.exclude(Q(geo_lat__isnull=True) | Q(geo_long__isnull=True) | Q(events__isnull=True)).prefetch_related('events')
	item_filters = Q()
	
	if request.user.is_superuser or request.user.is_staff:
		# Privileged User
		query = query.all()
	else:
		# Regular or anonymous user
		query = query.filter(Q(events__confirmed=True) | Q(events__date_start__gte=timezone.now()))
		item_filters = item_filters & (Q(confirmed=True) | Q(date_start__gte=timezone.now()))
	
	if not mature_check[0]:
		query = query.exclude(events__event__mature=True)
		item_filters = item_filters & Q(event__mature=False)
	
	if slug == 'full_list':
		pass
	elif 'filter_type' in slug:
		filter = slug.replace('filter_type_','')
		filter_obj = get_object_or_404(event_type, slug=filter)
		query = query.filter(events__event__type=filter_obj)
		item_filters = item_filters & Q(event__type=filter_obj)
	elif 'filter_flag' in slug:
		filter = slug.replace('filter_flag_','')
		filter_obj = get_object_or_404(attendance_flag, slug=filter)
		query = query.filter(events__flags=filter_obj)
		item_filters = item_filters & Q(flags=filter_obj)
	elif 'event_' in slug:
		filter = slug.replace('event_','')
		filter_obj = get_object_or_404(event, slug=filter)
		query = query.filter(events__event=filter_obj)
		item_filters = item_filters & Q(event=filter_obj)
	else:
		self.request.session['deerfind_norecover'] = True
		raise Http404
	
	for item in query:
		events = item.events.filter(item_filters).select_related('event', 'event__type', 'photos', 'report', 'report__cat').prefetch_related('flags').order_by('-date_start')
		event_names = []
		event_count = 0
		marker_color = '#3bb2d0'
		marker_symbol = None
		
		for subitem in events:
			if subitem.is_upcoming:
				extra_classes = ' event_upcoming'
			elif subitem.is_tentative:
				extra_classes = ' event_tentative'
			else:
				extra_classes = ''
			
			if subitem.flags or subitem.photos or subitem.report:
				flag_row = []
				
				if subitem.photos:
					flag_row.append('<a href="%s" class="blue"><img src="%simages/icons/camera.png" alt="%s" title="%s" /></a>' % (subitem.photos.get_absolute_url(), settings.STATIC_URL, subitem.photos.title, subitem.photos.title))
				
				if subitem.report:
					flag_row.append('<a href="%s" class="red"><img src="%simages/icons/book.png" alt="%s" title="%s" /></a>' % (subitem.report.get_absolute_url(), settings.STATIC_URL, subitem.report.get_title(), subitem.report.get_title()))
				
				for f in subitem.flags.all():
					flag_row.append('<a href="%s"><img src="%s" alt="%s" title="%s" /></a>' % (f.get_absolute_url(), f.get_icon_url(), f.name, f.name))
				
				flags = '<div class="hovericons16 item_flags">%s</div>' % ''.join(flag_row)
				margin_right = len(flag_row) * 24
				margin_right = margin_right + 10
			else:
				flags = ''
				margin_right = 0
			
			event_row = '<div class="event_row%s"><div class="event_name" style="margin-right:%dpx;"><a href="%s">%s</a> (%s)</div>%s</div>' % (extra_classes, margin_right, subitem.event.get_absolute_url(), subitem.get_name(), subitem.date_start.strftime('%b %d, %Y'), flags)
			
			event_names.append(event_row)
			event_count = event_count + 1
			if subitem.event.type.map_color:
				marker_color = '#%s' % subitem.event.type.map_color
			
			# This is where Mapbox's Maki markers would be used for the map marker for this venue.
			# Unfortunately, there doesn't seem to be any way to use them, currently.
			# Hopefully, this will change in the future.
			# if subitem.event.type.symbol:
				# marker_symbol = subitem.event.type.symbol
		
		if event_count > 3:
			marker_size='large'
		elif event_count < 2:
			marker_size='small'
		else:
			marker_size='medium'
		
		if not marker_symbol:
			marker_symbol = event_count
		
		return_data.append({
			'type':'Feature',
			'geometry': {
				'type':'Point', 
				'coordinates':[item.geo_long, item.geo_lat],
			},
			'properties': {
				'marker-symbol':marker_symbol, 
				'marker-color':marker_color,
				'marker-size':marker_size, 
				'title':'<a href="%s">%s</a><br /><span class="city">%s</span>' % (item.get_absolute_url(), item.name, item.get_city()),
				'description':'<div class="event_list_tooltip">%s</div>' % ' '.join(event_names)
			},
		})
	
	return json_response(request, data=return_data)
