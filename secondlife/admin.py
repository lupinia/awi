#	secondlife (Legacy Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from secondlife.models import security_control

class security_admin(admin.ModelAdmin):
	list_display=('name','grid','auth','key')
	list_filter=('auth','grid')

admin.site.register(security_control,security_admin)
