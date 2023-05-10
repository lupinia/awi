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

from awi_utils.utils import rand_license_plate
from awi_utils.sl_plates import plate_types

def json_response(request, data=''):
	return HttpResponse(simplejson.dumps(data), content_type='application/json')

class placeholder(TemplateView):
	def get_context_data(self, **kwargs):
		context=super(placeholder,self).get_context_data(**kwargs)
		return context

#	This is a tangentially-related convenience tool that I didn't have a better home for
class plate_generator(TemplateView):
	template_name = 'sl_plategen.html'
	
	def get_context_data(self, **kwargs):
		context=super(plate_generator,self).get_context_data(**kwargs)
		context['generated'] = False
		
		slug = kwargs.get('slug', '').lower()
		cur_plate = plate_types.get(slug.upper(), {})
		cur_plate_sequence = cur_plate.get('sequence', '')
		
		if cur_plate_sequence:
			context['slug'] = slug
			context['notes'] = cur_plate.get('notes', '')
			platevalue = rand_license_plate(cur_plate_sequence)
			if platevalue:
				context['generated'] = True
				context['platevalue'] = platevalue
		
		else:
			plate_codes = plate_types.keys()
			plate_codes.sort()
			context['plate_types'] = []
			for code in plate_codes:
				p = plate_types[code]
				p['code'] = code.upper()
				p['slug'] = code.lower()
				context['plate_types'].append(p)
		
		return context

#	A homepage for new tabs, to just show a photo background, plus some helpful extra data
class newtab_view(TemplateView):
	template_name = 'newtab_page.html'
	
	def get_context_data(self, **kwargs):
		context=super(newtab_view,self).get_context_data(**kwargs)
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
