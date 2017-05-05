#	DeerHealth (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from deerhealth.models import *

class pills_admin(admin.ModelAdmin):
	list_display=('name','fullname','per_day','remaining','end_date','last_update')
	fields=(('name','slug'),'fullname',('quantity','per_day'))
	prepopulated_fields = {"slug": ("name",)}
	ordering=['per_day','slug',]
	
	def save_model(self, request, obj, form, change):
		if not change:
			obj.owner = request.user
		obj.save()

admin.site.register(prescription,pills_admin)
