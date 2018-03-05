#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views (Sitewide)
#	=================

import simplejson

from django.http import HttpResponse
from django.views.generic import TemplateView

def json_response(request, data=''):
	return HttpResponse(simplejson.dumps(data), content_type='application/json')

class placeholder(TemplateView):
	def get_context_data(self, **kwargs):
		context=super(placeholder,self).get_context_data(**kwargs)
		return context
