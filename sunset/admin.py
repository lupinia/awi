#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.core.urlresolvers import reverse

from awi_access.admin import access_admin
from deerfind.admin import g2_inline
from deertrees.admin import leaf_admin
from sunset.models import (
	image,
	image_asset,
	image_meta,
	image_meta_key,
	batch_import,
	batch_image,
	batch_meta,
	background_tag
)

# Begin inlines
class asset_inline_admin(admin.TabularInline):
	model = image_asset
	extra = 0
	fields = ['type','image_file','timestamp_post','timestamp_mod',]
	readonly_fields = ['timestamp_post','timestamp_mod',]

class meta_inline_admin(admin.TabularInline):
	model = image_meta
	extra = 0
	fields = ['key','data','manual_entry']

class batch_meta_inline_admin(admin.TabularInline):
	model = batch_meta
	extra = 0
	fields = ['key','data']

class batch_image_inline_admin(admin.TabularInline):
	model = batch_image
	extra = 0
	fields = ['img_filename','img_obj','timestamp_mod','status',]
	readonly_fields = ['timestamp_mod','status',]

# End inlines, begin regular admin objects
class image_admin(leaf_admin):
	list_select_related = True
	search_fields = ['body','summary','title','basename'] + leaf_admin.search_fields
	fieldsets = [
		(None,{'fields':(('title','basename'),('summary','auto_fields','rebuild_assets'),'body','bg_tags',('crop_horizontal','crop_vertical',),),},),
	] + leaf_admin.fieldsets
	prepopulated_fields={'basename':('title',)}
	list_display = ('title','rebuild_assets','public_domain',) + leaf_admin.list_display
	inlines = leaf_admin.inlines + [g2_inline, asset_inline_admin, meta_inline_admin]
	list_filter = ['bg_tags','rebuild_assets','public_domain','auto_fields',] + leaf_admin.list_filter
	
	def view_on_site(self, obj):
		return reverse('image_single',kwargs={'cached_url':obj.cat.cached_url, 'slug':obj.basename,})

class image_meta_key_admin(admin.ModelAdmin):
	list_select_related = True
	search_fields = ('key','display_name',)
	list_display = ('key','display_name','format_type','public','ignore',)
	list_filter = ('ignore','public','format_type',)
	fields = ('key',('display_name','format_type'),('public','ignore'))
	actions = ['public','unpublic','ignore','unignore',]
	
	def public(self, request, queryset):
		rows_updated = queryset.update(public=True)
		if rows_updated == 1:
			message_bit = "1 key was"
		else:
			message_bit = "%s keys were" % rows_updated
		self.message_user(request, "%s successfully set as publicly displayed." % message_bit)
	
	def unpublic(self, request, queryset):
		rows_updated = queryset.update(public=False)
		if rows_updated == 1:
			message_bit = "1 key was"
		else:
			message_bit = "%s keys were" % rows_updated
		self.message_user(request, "%s successfully set as private." % message_bit)
	
	def ignore(self, request, queryset):
		# We can't ignore something without also setting it private
		rows_updated = queryset.update(ignore=True,public=False)
		if rows_updated == 1:
			message_bit = "1 key was"
		else:
			message_bit = "%s keys were" % rows_updated
		self.message_user(request, "%s successfully disabled from parsing and removed from public display." % message_bit)
	
	def unignore(self, request, queryset):
		rows_updated = queryset.update(ignore=False)
		if rows_updated == 1:
			message_bit = "1 key was"
		else:
			message_bit = "%s keys were" % rows_updated
		self.message_user(request, "%s successfully re-enabled for image file parsing." % message_bit)
	
	public.short_description = "Make selected keys public"
	unpublic.short_description = "Make selected keys private"
	ignore.short_description = "Disable parsing for selected keys"
	unignore.short_description = "Enable parsing for selected keys"

class batch_import_admin(access_admin):
	list_select_related = True
	search_fields = ['folder','title','basename','desc','cat__title','cat__slug','tags__title','tags__slug']
	list_display = ('folder_shortname','cat','active','sync_now','timestamp_mod',) + access_admin.list_display
	list_filter = access_admin.list_filter + ['timestamp_post','timestamp_mod','cat','tags','active']
	fieldsets = [
		('Batch Processor Options',{'fields': (('folder','next_sequence_number'),('active','sync_now',),),},),
		('Imported Image Options',{'fields': ('cat',('title','basename'),'desc','tags',),},),
		('Time Options',{'fields': (('timestamp_post','timestamp_mod',),),},),
	] + access_admin.fieldsets
	inlines = [batch_meta_inline_admin, batch_image_inline_admin]
	readonly_fields = ['timestamp_mod',]
	filter_horizontal = ['tags',]
	actions = ['activate', 'deactivate', 'sync_now'] + access_admin.actions
	
	def activate(self, request, queryset):
		rows_updated = queryset.update(active=True)
		if rows_updated == 1:
			message_bit = "1 folder"
		else:
			message_bit = "%s folders" % rows_updated
		self.message_user(request, "Synchronization was successfully activated for %s" % message_bit)
	
	def deactivate(self, request, queryset):
		rows_updated = queryset.update(active=False)
		if rows_updated == 1:
			message_bit = "1 folder"
		else:
			message_bit = "%s folders" % rows_updated
		self.message_user(request, "Synchronization was successfully deactivated for %s" % message_bit)
	
	def sync_now(self, request, queryset):
		rows_updated = queryset.update(sync_now=True)
		if rows_updated == 1:
			message_bit = "1 folder"
		else:
			message_bit = "%s folders" % rows_updated
		self.message_user(request, "%s prioritized to sync immediately" % message_bit)
	
	activate.short_description = "Activate selected folders"
	deactivate.short_description = "Deactivate selected folders"
	sync_now.short_description = "Sync selected folders immediately"

class bgtag_admin(admin.ModelAdmin):
	fields = ['title', 'tag', 'default']
	list_display = ['display_title', 'tag', 'default']

# Register admin objects
admin.site.register(image,image_admin)
admin.site.register(image_meta_key, image_meta_key_admin)
admin.site.register(batch_import, batch_import_admin)
admin.site.register(background_tag, bgtag_admin)