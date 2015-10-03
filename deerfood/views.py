#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.views import generic
from deerfood.models import menu_item

# Create your views here.
class full_menu(generic.ListView):
	model=menu_item
	context_object_name='menu_items'
	template_name='deerfood/full_menu.html'
	
	def get_queryset(self, *args, **kwargs):
		return menu_item.objects.all().order_by('section','name').prefetch_related('flags')