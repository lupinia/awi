#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.views import generic
from django.core.urlresolvers import reverse

from deerfood.models import menu_item

# Create your views here.
class full_menu(generic.ListView):
	model=menu_item
	context_object_name='menu_items'
	template_name='deerfood/full_menu.html'
	
	def get_queryset(self, *args, **kwargs):
		return menu_item.objects.all().order_by('section','name').prefetch_related('flags').select_related('section')
	
	def get_context_data(self, **kwargs):
		context=super(full_menu,self).get_context_data(**kwargs)
		
		from deertrees.models import special_feature
		menu_leaf = special_feature.objects.get(url='menu')
		
		ancestors = menu_leaf.cat.get_ancestors(include_self=True)
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		for crumb in ancestors:
			context['breadcrumbs'].append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
		
		context['breadcrumbs'].append({'url':reverse('deerfood:full_menu'), 'title':menu_leaf.title})
		
		return context
