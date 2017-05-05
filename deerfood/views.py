#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.views import generic
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import get_object_or_404

from deerfood.models import menu_item, menu_section, menu_flag
from deertrees.views import special_feature_view

class menu_item_list(special_feature_view):
	model=menu_item
	context_object_name='menu_items'
	template_name='deerfood/full_menu.html'
	
	def build_breadcrumbs(self, cur=False, cur_type=''):
		breadcrumbs = self.breadcrumbs()
		if breadcrumbs:
			if cur and cur_type:
				breadcrumbs.append({'url':reverse('deerfood:menu_'+cur_type, kwargs={'slug':cur.slug}), 'title':cur.name})
			
			return breadcrumbs
		else:
			return False
	
	def can_edit(self):
		if self.request.user.is_authenticated():
			if self.request.user.has_perm('deerfood.change_menu_item'):
				return True
			else:
				return False
		else:
			return False
	
	def get_filters(self):
		filters = {}
		filters['sections'] = menu_section.objects.all().order_by('name').annotate(num_items=Count('menu_item'))
		filters['flags'] = menu_flag.objects.all().order_by('name').annotate(num_items=Count('menu_item'))
		return filters


class full_menu(menu_item_list, generic.ListView):
	def get_queryset(self, *args, **kwargs):
		return menu_item.objects.all().order_by('section','name').prefetch_related('flags').select_related('section')
	
	def get_context_data(self, **kwargs):
		context=super(full_menu,self).get_context_data(**kwargs)
		context['breadcrumbs'] = self.build_breadcrumbs()
		context['filters'] = self.get_filters()
		context['can_edit'] = self.can_edit()
		return context


class menu_by_section(menu_item_list, generic.ListView):
	def get_queryset(self, *args, **kwargs):
		return menu_item.objects.filter(section__slug=self.kwargs['slug']).order_by('name').prefetch_related('flags').select_related('section')
	
	def get_context_data(self, **kwargs):
		context=super(menu_by_section,self).get_context_data(**kwargs)
		context['cur_filter'] = get_object_or_404(menu_section, slug=self.kwargs['slug'])
		context['cur_filter_type'] = 'section'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'section')
		context['filters'] = self.get_filters()
		context['can_edit'] = self.can_edit()
		return context


class menu_by_flag(menu_item_list, generic.ListView):
	def get_queryset(self, *args, **kwargs):
		return menu_item.objects.filter(flags__slug=self.kwargs['slug']).order_by('name').prefetch_related('flags').select_related('section')
	
	def get_context_data(self, **kwargs):
		context=super(menu_by_flag,self).get_context_data(**kwargs)
		context['cur_filter'] = get_object_or_404(menu_flag, slug=self.kwargs['slug'])
		context['cur_filter_type'] = 'flag'
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'flag')
		context['filters'] = self.get_filters()
		context['can_edit'] = self.can_edit()
		return context

