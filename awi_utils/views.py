#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views (Sitewide)
#	=================

import random
import simplejson

from string import ascii_uppercase

from django.http import HttpResponse
from django.views.generic import TemplateView

from awi_utils.utils import rand_int_list

def json_response(request, data=''):
	return HttpResponse(simplejson.dumps(data), content_type='application/json')

class placeholder(TemplateView):
	def get_context_data(self, **kwargs):
		context=super(placeholder,self).get_context_data(**kwargs)
		return context

#	This is a quickly-built convenience tool that I didn't have a better home for
class plate_generator(TemplateView):
	template_name = 'sl_plategen.html'
	
	def get_context_data(self, **kwargs):
		context=super(plate_generator,self).get_context_data(**kwargs)
		
		platetype = kwargs.get('platetype', '').lower()
		context['platetype'] = platetype
		platevalue = ''
		plate_values = []
		letter_range = ascii_uppercase.replace('I', '')
		letter_range = letter_range.replace('O', '')
		
		if platetype == 'fdci-cr':
			plate_values.append(random.choice(letter_range))
			second_letter = random.choice(letter_range)
			
			# Try to minimize duplicates
			if second_letter == plate_values[0]:
				second_letter = random.choice(letter_range)
			plate_values.append(second_letter)
			
			plate_values += rand_int_list(3, first_zero=True)
			platevalue = ''.join(map(str, plate_values))
		
		elif platetype == 'fdci-pj':
			plate_values = rand_int_list(3)
			platevalue = 'J-%s' % ''.join(map(str, plate_values))
		
		elif platetype == 'fdci-vb':
			platevalue = ''.join(map(str, rand_int_list(3)))
		
		if platevalue:
			context['generated'] = True
			context['platevalue'] = platevalue
		else:
			context['generated'] = False
		
		return context
