#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views (Sitewide)
#	=================

import pytz

from datetime import datetime

from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone


#	A homepage for new tabs, to just show a photo background, plus some helpful extra data
class newtab_view(TemplateView):
	template_name = 'newtab_page.html'
	
	def get_context_data(self, **kwargs):
		context=super(newtab_view,self).get_context_data(**kwargs)
		context['title_page'] = "New Tab"
		context['newtab'] = True
		context['time_local'] = timezone.now()
		context['clock_sync'] = (60 - context['time_local'].second) * 1000
		if settings.NEWTAB_CLOCK_LIST:
			context['time_list'] = []
			for label, zone in settings.NEWTAB_CLOCK_LIST:
				context['time_list'].append(
					{'label': label,
					'timestamp': datetime.now(pytz.timezone(zone))}
				)
		
		return context
