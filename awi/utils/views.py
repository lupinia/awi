#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for Django views and responses
#	=================

import simplejson

from django.http import HttpResponse
from django.views.generic import TemplateView


def json_response(request, data=''):
	"""Basic JSON output view"""
	return HttpResponse(simplejson.dumps(data), content_type='application/json')

class placeholder(TemplateView):
	"""Blank template view"""
	def get_context_data(self, **kwargs):
		context=super(placeholder,self).get_context_data(**kwargs)
		return context
