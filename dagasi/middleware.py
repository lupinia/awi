#	Dagasi - Content Security (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Middleware
#	=================

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from dagasi.utils.users import default_userprefs

class UserPrefsMiddleware(MiddlewareMixin):
	# Standard request handling
	def process_request(self, request):
		if request.session.get('userprefs', None):
			# If we already customized something, pull it from the session data
			request.userprefs = request.session['userprefs']
		
		elif request.user.is_authenticated():
			# Logged-in users are easy, just pull from user settings
			request.session['userprefs'] = request.user.settings.as_dict()
			request.userprefs = request.session['userprefs']
		
		else:
			# No existing session data, and no user, so we'll use sensible defaults
			request.userprefs = default_userprefs()
