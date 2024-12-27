#	DeerBuild - Virtual World Creator Tools (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin

from deerbuild.models import license_plate_region_group, license_plate_region, license_plate

class plate_region_group_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(('name','slug',),'notes',),},),
		('System Options', {'fields':(('active','timestamp_post','timestamp_mod',),),},),
	]
	
	list_filter = ('active','timestamp_post','timestamp_mod',)
	list_display = ('name','slug','active','timestamp_post','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('name','slug','notes',)

class plate_region_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(('name','code','group',),'notes',),},),
		('System Options', {'fields':(('active','timestamp_post','timestamp_mod',),),},),
	]
	
	list_select_related = True
	list_filter = ('group','active','timestamp_post','timestamp_mod',)
	list_display = ('name','code','group','active','timestamp_post','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('name','code','notes',)

class plate_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(('design_name','design_code','territory',),'sequence','notes',),},),
		('System Options', {'fields':(('can_generate','active',),('timestamp_post','timestamp_mod',),),},),
	]
	
	list_select_related = True
	list_filter = ('territory__group','territory','can_generate','active','timestamp_post','timestamp_mod',)
	list_display = ('name','code','sample','can_generate','active','timestamp_post','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('design_name','design_code','notes',)

admin.site.register(license_plate_region_group, plate_region_group_admin)
admin.site.register(license_plate_region, plate_region_admin)
admin.site.register(license_plate, plate_admin)
