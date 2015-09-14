from django.contrib import admin
from deerhealth.models import *

class pills_admin(admin.ModelAdmin):
	list_display=('name','per_day','remaining','end_date')
	fields=(('name','slug'),('quantity','per_day'))
	prepopulated_fields = {"slug": ("name",)}
	
	def save_model(self, request, obj, form, change):
		if not change:
			obj.owner = request.user
		obj.save()

admin.site.register(prescription,pills_admin)