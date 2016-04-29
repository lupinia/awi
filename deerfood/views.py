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

from deerfood.models import menu_item, menu_section, menu_flag
from deertrees.models import special_feature

class menu_item_list():
	model=menu_item
	context_object_name='menu_items'
	template_name='deerfood/full_menu.html'
	
	def build_breadcrumbs(self, cur=False, cur_type=''):
		breadcrumbs = []
		menu_leaf = special_feature.objects.get(url='menu')
		ancestors = menu_leaf.cat.get_ancestors(include_self=True)
		
		for crumb in ancestors:
			breadcrumbs.append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
		
		breadcrumbs.append({'url':reverse('deerfood:full_menu'), 'title':menu_leaf.title})
		
		if cur and cur_type:
			breadcrumbs.append({'url':reverse('deerfood:menu_'+cur_type, kwargs={'slug':cur.slug}), 'title':cur.name})
		
		return breadcrumbs
	
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
		return context


class menu_by_section(menu_item_list, generic.ListView):
	def get_queryset(self, *args, **kwargs):
		return menu_item.objects.filter(section__slug=self.kwargs['slug']).order_by('name').prefetch_related('flags').select_related('section')
	
	def get_context_data(self, **kwargs):
		context=super(menu_by_section,self).get_context_data(**kwargs)
		context['cur_filter'] = menu_section.objects.get(slug=self.kwargs['slug'])
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'section')
		context['filters'] = self.get_filters()
		return context


class menu_by_flag(menu_item_list, generic.ListView):
	def get_queryset(self, *args, **kwargs):
		return menu_item.objects.filter(flags__slug=self.kwargs['slug']).order_by('name').prefetch_related('flags').select_related('section')
	
	def get_context_data(self, **kwargs):
		context=super(menu_by_flag,self).get_context_data(**kwargs)
		context['cur_filter'] = menu_flag.objects.get(slug=self.kwargs['slug'])
		context['breadcrumbs'] = self.build_breadcrumbs(context['cur_filter'], 'flag')
		context['filters'] = self.get_filters()
		return context

