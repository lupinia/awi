#	DeerLand - Virtual World Property Management (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.core.urlresolvers import reverse

from deerland.models import estate, region

class region_inline(admin.TabularInline):
	model = region
	extra = 0
	ordering = ('name',)
	verbose_name_plural = "Regions"
	readonly_fields = ('timestamp_mod',)
	fields = ('name', 'rating', 'is_active', 'data_pos_x', 'data_pos_y', 'timestamp_post', 'timestamp_mod',)

class estate_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(('name','slug',),'description',),},),
		('System Options', {'fields':(('owner','grid',),('timestamp_post','timestamp_mod',),),},),
	]
	
	list_select_related = True
	list_filter = ('grid',)
	list_display = ('name','owner','grid','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('name','slug','description',)
	inlines=[region_inline, ]

class region_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(('name','estate',),'notes',),},),
		('System Options', {'fields':(('rating','is_active',),('data_pos_x','data_pos_y',),('timestamp_post','timestamp_mod',),),},),
	]
	
	list_select_related = True
	list_filter = ('rating','is_active',)
	list_display = ('name','estate','rating','is_active','timestamp_mod','timestamp_post','timestamp_check',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('name','notes',)

admin.site.register(estate, estate_admin)
admin.site.register(region, region_admin)
