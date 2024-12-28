#	DeerBuild - Virtual World Creator Tools (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.db.models import Count
from django.http import Http404
from django.views.generic import ListView, DetailView

from deerbuild.models import license_plate, license_plate_region_group

class plate_generator(DetailView):
	model = license_plate
	slug_field = 'design_code'
	slug_url_kwarg = 'code'
	template_name = 'deerbuild/plategen.html'
	
	def get_queryset(self, *args, **kwargs):
		if self.kwargs.get('territory', False):
			queryset = super(plate_generator, self).get_queryset(*args, **kwargs).select_related('territory', 'territory__group')
			if not self.request.user.is_superuser:
				queryset = queryset.filter(active=True, territory__active=True, territory__group__active=True)
			return queryset.filter(territory__code=self.kwargs['territory'])
		else:
			return self.model.objects.none()
	
	def get_context_data(self, **kwargs):
		context=super(plate_generator,self).get_context_data(**kwargs)
		
		if context['object'].can_generate:
			context['title_page'] = "License Plate Generator: %s" % context['object'].code
		else:
			context['title_page'] = "License Plate Details: %s" % context['object'].code
		
		return context

class plate_generator_list(DetailView):
	model = license_plate_region_group
	slug_field = 'slug'
	slug_url_kwarg = 'group'
	template_name = 'deerbuild/platelist.html'
	
	def get_queryset(self, *args, **kwargs):
		if self.kwargs.get('group', False):
			queryset = super(plate_generator_list, self).get_queryset(*args, **kwargs).prefetch_related('plate_regions', 'plate_regions__plates')
			if not self.request.user.is_superuser:
				queryset = queryset.filter(active=True)
			
			return queryset
		
		else:
			return self.model.objects.none()
	
	def get_context_data(self, **kwargs):
		context=super(plate_generator_list,self).get_context_data(**kwargs)
		
		context['title_page'] = "License Plate Generators: %s" % context['object'].name
		
		return context

class plate_generator_root(ListView):
	model = license_plate_region_group
	template_name = 'deerbuild/plategroups.html'
	
	def get_queryset(self, *args, **kwargs):
		queryset = super(plate_generator_root, self).get_queryset(*args, **kwargs)
		if not self.request.user.is_superuser:
			queryset = queryset.filter(active=True)
		return queryset.annotate(plate_count=Count('plate_regions__plates'))
	
	def get_context_data(self, **kwargs):
		context=super(plate_generator_root,self).get_context_data(**kwargs)
		context['title_page'] = "License Plate Generators"
		context['expand_list'] = False
		
		return context
