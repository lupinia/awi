#	User Account Tools (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.core.urlresolvers import reverse

from usertools.models import person, group

class person_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(
			('display_name','grid_username',),
			'profile_text',
			'notes',
		),},),
		('Options', {'fields':(
			('account','key','is_bot',),
			('date_gridcreate','grid',),
			('timestamp_post','timestamp_mod',),
		),},),
	]
	
	list_select_related = True
	list_filter = ('grid','is_bot',)
	list_display = ('display_name','grid_name','key','is_bot','grid','date_gridcreate','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('display_name','grid_username','grid_name_first','grid_name_last','notes','profile_text',)

class group_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(
			('name','key',),
			'description',
		),},),
		('Options', {'fields':(
			('owner','grid',),
			('timestamp_post','timestamp_mod',),
		),},),
	]
	
	list_select_related = True
	list_filter = ('grid',)
	list_display = ('name','key','owner','grid','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('name','description',)

admin.site.register(person, person_admin)
admin.site.register(group, group_admin)
