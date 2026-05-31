#	DeerSky - Digital Almanac and Weather Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.views.generic import DetailView, ListView
from django.core.urlresolvers import reverse
from django.db.models import Q

from deersky.models import homepage

#	Customizable homepage view showing a photo background and clocks
class homepage_view(DetailView):
	model = homepage
	template_name = 'deersky/newtab_view.html'
	
	def get_context_data(self, **kwargs):
		context = super(homepage_view,self).get_context_data(**kwargs)
		
		context['newtab'] = True
		context['bg_tag'] = context['homepage'].get_bg_tag()
		context['title_page'] = context['homepage'].title
		context['time_local'] = context['homepage'].city.now()
		context['time_list'] = context['homepage'].secondary_clocks
		context['shortlink'] = context['homepage'].get_short_url(self.request)
		
		return context

class homepage_list(ListView):
	model = homepage
	template_name = 'deersky/newtab_list.html'
	
	def get_queryset(self):
		queryset = super(homepage_list, self).get_queryset()
		ordering = ['main_city__label',]
		if self.request.user.is_authenticated():
			if not self.request.user.is_superuser and not self.request.user.is_staff:
				# Regular user
				queryset = queryset.filter(Q(public=True) | Q(owner=self.request.user))
				ordering.insert(0, 'public') # Put all private items at the top as a convenience
		else:
			queryset = queryset.filter(public=True)
		
		return queryset.select_related('main_city', 'owner').prefetch_related('secondary_clock_set', 'backgrounds_override').order_by(*ordering)
	
	def get_context_data(self, **kwargs):
		context = super(homepage_list, self).get_context_data(**kwargs)
		
		context['title_view'] = 'Homepages'
		
		# Breadcrumbs
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		context['breadcrumbs'].append({'url':reverse('deersky:newtab_list'), 'title':'Homepages'})
		
		# Metadata
		context['title_page'] = context['title_view']
		context['sitemeta_desc'] = "Basic photo-background homepages with clocks and timer widgets, no ads or upsells, just a simple utility service."
		
		return context
