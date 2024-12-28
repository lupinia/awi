#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views (Sitewide)
#	=================

import pytz
import simplejson

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils import timezone

def json_response(request, data=''):
	return HttpResponse(simplejson.dumps(data), content_type='application/json')

class placeholder(TemplateView):
	def get_context_data(self, **kwargs):
		context=super(placeholder,self).get_context_data(**kwargs)
		return context


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
