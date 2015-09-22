#	Awi Access (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	Extend admin_access to gain admin features specific to this app.
#	=================

from django.contrib.admin import ModelAdmin
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import ManyToManyField

from awi_access.models import access_control

class access_admin(ModelAdmin):
	fieldsets = [('Security Options',{'fields': (('published','featured','mature','sites','security'),),},),]
	list_filter=['published','featured','mature','sites','security','owner']
	#formfield_overrides = {ManyToManyField: {'widget':CheckboxSelectMultiple,},}
	
	def save_model(self, request, obj, form, change):
		if not change:
			obj.owner = request.user
		obj.save()
	
	class Media:
		js=['js/foldable-list-filter.js',]
		css={'all':['css/foldable-list-filter.css',],}
