from django.contrib.admin import ModelAdmin
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import ManyToManyField

from awi_access.models import access_control

class access_admin(ModelAdmin):
	fieldsets = [('Security Options',{'fields': (('published','featured','mature','sites','security'),),},),]
	list_filter=['published','featured','mature','sites','security','owner']
	formfield_overrides = {ManyToManyField: {'widget':CheckboxSelectMultiple,},}
	
	def save_model(self, request, obj, form, change):
		if not change:
			obj.owner = request.user
		obj.save()
