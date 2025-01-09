#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from deerfood.models import menu_item, menu_flag, menu_section

admin.site.register(menu_item)
admin.site.register(menu_section)
admin.site.register(menu_flag)