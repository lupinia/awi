#	DeerGuard SL (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.core.urlresolvers import reverse

from deerguard_sl.models import security_system, security_server, security_zone

class security_zone_inline(admin.TabularInline):
	model = security_zone
	extra = 0
	ordering = ('slug',)
	verbose_name_plural = "Security Zones"
	fields = ('name', 'slug', 'auth_public', 'auth_samegroup', 'auth_private', 'log_allowed', 'log_denied',)

class security_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(('name','slug',),'notes',('timestamp_post','timestamp_mod',),),},),
		('System Configuration', {'fields':(('owner','grid',),('channel_devices','channel_servers',),'system_admins',),},),
	]
	
	list_select_related = True
	list_filter = ('grid',)
	list_display = ('name','owner','grid','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	filter_horizontal = ['system_admins',]
	search_fields = ('name','slug','notes',)

class zone_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':('system',('name','slug',),'notes',('timestamp_post','timestamp_mod',),),},),
		('Configuration', {'fields':(('auth_public','auth_samegroup','auth_private',),('log_allowed','log_denied',),),},),
		('Authentication Lists', {'fields':('auth_users_allowed','auth_users_denied','auth_groups_allowed','auth_groups_denied',),},),
	]
	
	list_select_related = True
	list_filter = ('system','auth_public','auth_samegroup','auth_private',)
	list_display = ('name','system','auth_public','auth_samegroup','auth_private','log_allowed','log_denied','timestamp_mod',)
	readonly_fields = ['timestamp_mod','system',]
	filter_horizontal = ['auth_users_allowed','auth_users_denied','auth_groups_allowed','auth_groups_denied',]
	search_fields = ('name','slug','notes',)

admin.site.register(security_system, security_admin)
admin.site.register(security_zone, zone_admin)
