#	Awi Access (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	Extend admin_access to gain admin features specific to this app.
#	=================

from django.contrib.admin import ModelAdmin
from django.db.models import ManyToManyField

from awi_access.models import access_control

class access_admin(ModelAdmin):
	fieldsets = [('Security Options',{'fields': (('published','featured','mature','sites','security'),),},),]
	list_filter=['published','featured','mature','sites','security','owner']
	list_display = ('published','featured','mature','security',)
	actions = ['publish','unpublish','feature','unfeature',]
	
	def save_model(self, request, obj, form, change):
		if not change:
			obj.owner = request.user
		obj.save()
	
	def publish(self, request, queryset):
		rows_updated = queryset.update(published=True)
		if rows_updated == 1:
			message_bit = "1 item was"
		else:
			message_bit = "%s items were" % rows_updated
		self.message_user(request, "%s successfully published." % message_bit)
	
	def unpublish(self, request, queryset):
		rows_updated = queryset.update(published=False)
		if rows_updated == 1:
			message_bit = "1 item was"
		else:
			message_bit = "%s items were" % rows_updated
		self.message_user(request, "%s successfully unpublished." % message_bit)
	
	def feature(self, request, queryset):
		rows_updated = queryset.update(featured=True)
		if rows_updated == 1:
			message_bit = "1 item was"
		else:
			message_bit = "%s items were" % rows_updated
		self.message_user(request, "%s successfully marked as featured." % message_bit)
	
	def unfeature(self, request, queryset):
		rows_updated = queryset.update(featured=False)
		if rows_updated == 1:
			message_bit = "1 item was"
		else:
			message_bit = "%s items were" % rows_updated
		self.message_user(request, "%s successfully marked as not featured." % message_bit)
	
	publish.short_description = "Publish selected items"
	unpublish.short_description = "Unpublish selected items"
	feature.short_description = "Feature selected items"
	unfeature.short_description = "Unfeature selected items"
	
	class Media:
		js=['js/foldable-list-filter.js',]
		css={'all':['css/foldable-list-filter.css',],}
