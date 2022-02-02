#	GridUtils - Virtual World Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.core.urlresolvers import reverse

from gridutils.models import (
	grid,
	avatar,
	group,
	group_role,
	estate,
	region,
	parcel,
	parcel_stream,
)

# Begin inlines
class group_role_inline_admin(admin.TabularInline):
	model = group_role
	max_num = 10
	min_num = 2
	extra = 0
	fields = ['role_name','role_title','is_everyone','is_owner','key','timestamp_post',]
	ordering = ['-is_owner','-is_everyone','role_name',]


# End inlines, begin extendable admin objects
class location_admin_base(admin.ModelAdmin):
	fieldsets = [('Coordinates', {'fields':(('location_x','location_y','location_z',),'coords_vector',),},),]
	readonly_fields = ['coords_vector',]


# End includable, begin regular admin objects
class person_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(
			('display_name','grid_username',),
			('key','active','is_bot',),
			('grid','date_gridcreate',),
		),},),
		('Profile: Basic', {'fields':(
			('icon_key','is_mature','web_publish',),
			('grid_verified','grid_paid','grid_employee',),
			('profile_url','profile_languages',),
			'profile_text',
			'profile_firstlife',
		),},),
		('Profile: Wants', {'fields':(
			('wantto_build','wantto_explore',),
			('wantto_meet','wantto_work',),
			('wantto_group','wantto_buy',),
			('wantto_sell','wantto_hire',),
			'profile_wants',
		),},),
		('Profile: Skills', {'fields':(
			('skills_textures','skills_architecture',),
			('skills_modeling','skills_events',),
			('skills_scripting','skills_characters',),
			'profile_skills',
		),},),
		('System Options', {'fields':(
			('account','primary_for_account','allow_gridlogin',),
			('timestamp_post','timestamp_mod','timestamp_sync',),
			'notes',
		),},),
	]
	
	list_select_related = True
	list_filter = ('grid','active','is_bot','grid_verified','grid_paid','grid_employee','allow_gridlogin',)
	list_display = ('display_name','grid_name','key','is_bot','grid','date_gridcreate','timestamp_sync','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('display_name','grid_username','grid_name_first','grid_name_last','notes','profile_text','profile_firstlife',)

class group_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(
			('name','slug',),
			('grid','key','active',),
		),},),
		('Group Profile', {'fields':(
			('founder','icon_key',),
			('is_public','is_open','is_mature',),
			('signup_fee','member_count',),
			'description',
		),},),
		('System Options', {'fields':(
			('timestamp_post','timestamp_mod','timestamp_sync',),
			'notes',
		),},),
	]
	
	list_select_related = True
	list_filter = ('grid','active','is_public','is_open','is_mature',)
	list_display = ('name','grid','is_public','is_open','is_mature','active','timestamp_sync','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('name','slug','description','notes',)
	inlines = [group_role_inline_admin,]

class group_role_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(
			('parent','key',),
			('role_name','role_title',),
			'description',
			'members',
		),},),
		('System Options', {'fields':(
			('is_everyone','is_owner',),
			('timestamp_post','timestamp_mod','timestamp_sync',),
		),},),
	]
	
	list_select_related = True
	list_filter = ('is_everyone','is_owner',)
	list_display = ('role_name','role_title','parent','is_everyone','is_owner','timestamp_sync','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('role_name','role_title','description',)

class estate_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(
			('name','slug',),
			('grid','grid_estate_id',),
			'owner',
		),},),
		('Estate Details', {'fields':(
			'covenant',
			'description',
		),},),
		('System Options', {'fields':(
			('is_mainland','is_rental','default_estate'),
			('timestamp_post','timestamp_mod','timestamp_sync',),
		),},),
	]
	
	list_select_related = True
	list_filter = ('grid','is_mainland','is_rental','default_estate',)
	list_display = ('name','owner','grid','is_mainland','is_rental','default_estate','timestamp_sync','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('name','slug','description','covenant',)

class region_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(
			('name','slug',),
			'estate',
		),},),
		('Region Details', {'fields':(
			('rating','region_type',),
			('data_gridpos_x','data_gridpos_y',),
			'map_image',
			('release_channel_reported','release_channel_override',),
			('release_version','timestamp_restart',),
			'hostname',
		),},),
		('Landing Spot', {'fields':(
			('location_x','location_y','location_z',),
		),},),
		('System Options', {'fields':(
			('status','active',),
			('timestamp_post','timestamp_mod','timestamp_sync',),
			'notes',
		),},),
	]
	
	list_select_related = True
	list_filter = ('active','status','rating',)
	list_display = ('name','estate','rating','active','status','timestamp_restart','timestamp_sync','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('name','slug','description','covenant',)


admin.site.register(avatar, person_admin)
admin.site.register(group, group_admin)
admin.site.register(group_role, group_role_admin)
admin.site.register(estate, estate_admin)
admin.site.register(region, region_admin)
