#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views (Sitewide)
#	=================

import simplejson

from django.http import HttpResponse

def json_response(request, data=''):
	return HttpResponse(simplejson.dumps(data), content_type='application/json')