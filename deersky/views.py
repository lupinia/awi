#	DeerSky - Digital Almanac and Weather Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.views.generic import DetailView

from deersky.models import homepage

#	Customizable homepage view showing a photo background and clocks
class homepage_view(DetailView):
	model = homepage
	template_name = 'deersky/newtab_view.html'
	
	def get_context_data(self, **kwargs):
		context = super(homepage_view,self).get_context_data(**kwargs)
		
		context['newtab'] = True
		context['title_page'] = context['homepage'].title
		context['time_local'] = context['homepage'].city.now()
		context['time_list'] = context['homepage'].secondary_clocks
		
		return context
