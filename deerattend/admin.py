#	DeerAttend (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from deerattend.models import attendance_flag, event, event_instance, event_type, venue

admin.site.register(venue)
admin.site.register(attendance_flag)
admin.site.register(event_type)
admin.site.register(event)
admin.site.register(event_instance)
