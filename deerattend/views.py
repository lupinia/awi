#	DeerAttend (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.utils import timezone
from django.views import generic

from deerattend.models import *
from deertrees.models import special_feature

class event_list():
	model=event_instance
	context_object_name='event_instances'
	template_name='deerattend/event_list.html'
	
	special_filters = {
		'photos':{'name':'Events with Photos', 'slug':'photos', 'filter':Q(photos__isnull=False), 'is_mature':False, },
		'reports':{'name':'Events with Reports', 'slug':'reports', 'filter':Q(report__isnull=False), 'is_mature':False, },
		'upcoming':{'name':'Confirmed Upcoming Appearances', 'slug':'upcoming', 'filter':Q(confirmed=True) & Q(date_start__gte=timezone.now()), 'is_mature':False, },
		'tentative':{'name':'Tentative Upcoming Appearances', 'slug':'tentative', 'filter':Q(confirmed=False) & Q(date_start__gte=timezone.now()), 'is_mature':False, },
		'mature':{'name':'Mature (18+)', 'slug':'mature', 'filter':Q(event__mature=True), 'is_mature':True, },
		'no-mature':{'name':'Hide Mature', 'slug':'no-mature', 'filter':Q(event__mature=False), 'is_mature':True, },
	}
	
	def filtered_queryset(self, *args, **kwargs):
		if self.request.user.is_authenticated():
			if not self.request.user.is_superuser or not self.request.user.is_staff:
				# Regular User
				queryset = event_instance.objects.filter(event__mature=False)
			else:
				# Privileged User
				queryset = event_instance.objects.all()
		else:
			# Anonymous User
			queryset = event_instance.objects.filter(Q(event__mature=False) & (Q(confirmed=True) | Q(date_start__gte=timezone.now())))
		
		return queryset.order_by('-date_start').prefetch_related('flags').select_related('event','event__type','venue','photos','report')
	
	def build_breadcrumbs(self, cur=False, cur_type=''):
		breadcrumbs = []
		cons_leaf = special_feature.objects.get(url='cons')
		ancestors = cons_leaf.cat.get_ancestors(include_self=True)
		
		for crumb in ancestors:
			breadcrumbs.append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
		
		breadcrumbs.append({'url':reverse('deerattend:full_list'), 'title':cons_leaf.title})
		
		if cur and cur_type:
			if cur_type == 'special':
				breadcrumbs.append({'url':reverse('deerattend:filter_'+cur_type, kwargs={'slug':cur['slug']}), 'title':cur['name']})
			else:
				breadcrumbs.append({'url':reverse('deerattend:filter_'+cur_type, kwargs={'slug':cur.slug}), 'title':cur.name})
		
		return breadcrumbs
	
	def can_edit(self):
		if self.request.user.is_authenticated():
			if self.request.user.has_perm('deertrees.change_event'):
				return True
			else:
				return False
		else:
			return False
	
	def get_filters(self):
		if self.request.user.is_authenticated():
			if not self.request.user.is_superuser or not self.request.user.is_staff:
				# Regular User
				type_query = event_type.objects.filter(event__mature=False)
				flag_query = attendance_flag.objects.filter(event__mature=False)
			else:
				# Privileged User
				type_query = event_type.objects.all()
				flag_query = attendance_flag.objects.all()
		else:
			# Anonymous User
			type_query = event_type.objects.filter(Q(event__mature=False) & (Q(event__event_instance__confirmed=True) | Q(event__event_instance__date_start__gte=timezone.now())))
			flag_query = attendance_flag.objects.filter(Q(event_instance__event__mature=False) & (Q(event_instance__confirmed=True) | Q(event_instance__date_start__gte=timezone.now())))
		
		filters = {}
		filters['types'] = type_query.order_by('name').annotate(num_items=Count('event__event_instance'))
		filters['flags'] = flag_query.order_by('name').annotate(num_items=Count('event_instance'))
		filters['special'] = []
		for slug, special in self.special_filters.iteritems():
			if special.get('is_mature',False):
				if self.request.user.is_authenticated() and (self.request.user.is_superuser or self.request.user.is_staff):
					filters['special'].append(special)
			else:
				filters['special'].append(special)
		return filters


class full_list(event_list, generic.ListView):
	def get_queryset(self, *args, **kwargs):
		return self.filtered_queryset(*args, **kwargs)
	
	def get_context_data(self, **kwargs):
		context=super(full_list,self).get_context_data(**kwargs)
		context['breadcrumbs'] = self.build_breadcrumbs()
		context['filters'] = self.get_filters()
		
		last_update = event_instance.objects.all().values('timestamp_mod').latest('timestamp_mod')
		context['update_time'] = last_update.get('timestamp_mod', False)
		context['filters_special'] = context['filters']['special']
		context['can_edit'] = self.can_edit()
		return context


class events_by_type(event_list, generic.ListView):
	def get_queryset(self, *args, **kwargs):
		return self.filtered_queryset(*args, **kwargs).filter(event__type__slug=self.kwargs['slug'])
	
	def get_context_data(self, **kwargs):
		context=super(events_by_type,self).get_context_data(**kwargs)
		context['cur_filter'] = event_type.objects.get(slug=self.kwargs['slug'])
		context['cur_filter_type'] = 'type'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'type')
		context['filters'] = self.get_filters()
		context['can_edit'] = self.can_edit()
		return context


class events_by_flag(event_list, generic.ListView):
	def get_queryset(self, *args, **kwargs):
		return self.filtered_queryset(*args, **kwargs).filter(flags__slug=self.kwargs['slug'])
	
	def get_context_data(self, **kwargs):
		context=super(events_by_flag,self).get_context_data(**kwargs)
		context['cur_filter'] = attendance_flag.objects.get(slug=self.kwargs['slug'])
		context['cur_filter_type'] = 'flag'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'flag')
		context['filters'] = self.get_filters()
		context['can_edit'] = self.can_edit()
		return context


class events_by_special(event_list, generic.ListView):
	def get_queryset(self, *args, **kwargs):
		if self.special_filters.get(self.kwargs['slug'], False):
			return self.filtered_queryset(*args, **kwargs).filter(self.special_filters[self.kwargs['slug']].get('filter', Q()))
		else:
			return self.filtered_queryset(*args, **kwargs)
	
	def get_context_data(self, **kwargs):
		context=super(events_by_special,self).get_context_data(**kwargs)
		context['cur_filter'] = self.special_filters.get(self.kwargs['slug'], False)
		context['cur_filter_type'] = 'special'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'special')
		context['filters'] = self.get_filters()
		context['can_edit'] = self.can_edit()
		return context


def widget(parent=False, parent_type=False, request=False):
	if request:
		queryset = event_instance.objects.filter(date_start__gte=timezone.now())
		if request.user.is_authenticated():
			if not request.user.is_superuser or not request.user.is_staff:
				# Regular User
				queryset = queryset.filter(event__mature=False)
		else:
			# Anonymous User
			queryset = queryset.filter(Q(event__mature=False))
		
		events_list = queryset.order_by('date_start').prefetch_related('flags').select_related('event','event__type','venue','photos','report')[:10]
		
		if events_list:
			return events_list
		else:
			return False
	else:
		return False
