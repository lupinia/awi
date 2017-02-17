#	Awi Error (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from awi_error.models import error

class error_admin(admin.ModelAdmin):
	list_display = ('error_key', 'message', 'severity', 'js_error',)
	list_filter = ('severity', 'js_error',)
	ordering = ('error_key',)
	search_fields = ['message','error_key']
	fields = ('error_key', ('severity', 'js_error', ), 'message',)

admin.site.register(error, error_admin)