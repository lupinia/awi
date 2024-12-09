#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.core.urlresolvers import reverse

from deertrees.admin import leaf_admin
from awi_access.admin import access_admin

from deerconnect.models import *

class link_admin(leaf_admin):
	list_select_related = True
	search_fields = ['label','url','desc'] + leaf_admin.search_fields
	fieldsets = [
		(None,{'fields':(('label','involved'),'url','desc','icon','icon_large'),},),
		('Health Check Options',{'fields':(('health_check','healthy'),),},),
	] + leaf_admin.fieldsets
	list_filter = leaf_admin.list_filter + ['involved', 'healthy']
	list_display = ('label','url','involved','healthy',) + leaf_admin.list_display
	readonly_fields = ['healthy',] + leaf_admin.readonly_fields
	
	def view_on_site(self, obj):
		return obj.url
	
	def save_model(self, request, obj, form, change):
		obj.healthy = True
		super(link_admin, self).save_model(request, obj, form, change)

class contact_admin(access_admin):
	list_select_related = True
	search_fields = ['label','name','url','desc']
	fieldsets = [
		(None,{'fields':(('label','name','im'),'url','desc','icon','icon_large','cat'),},),
		('Time Options',{'fields':(('timestamp_post','timestamp_mod',),),},),
	] + access_admin.fieldsets
	list_filter = access_admin.list_filter + ['im',]
	list_display = ('label','name','url','cat','im','timestamp_post','timestamp_mod',) + access_admin.list_display
	readonly_fields = ['timestamp_mod',]
	
	def view_on_site(self, obj):
		return obj.url

class spam_admin(admin.ModelAdmin):
	search_fields = ['word', 'notes']
	list_filter = ['active', 'case_sensitive', 'timestamp_post', 'timestamp_mod',]
	list_display = ['word', 'active', 'case_sensitive', 'timestamp_post', 'timestamp_mod',]
	readonly_fields = ['timestamp_mod',]
	fieldsets = [
		(None,{'fields':('word',('case_sensitive','active',),'notes',),},),
		('Time Options',{'fields':(('timestamp_post','timestamp_mod',),),},),
	]
	actions = ['case_on', 'case_off',]
	
	def case_on(self, request, queryset):
		rows_updated = queryset.update(case_sensitive=True)
		if rows_updated == 1:
			message_bit = "1 word"
		else:
			message_bit = "%s words" % rows_updated
		self.message_user(request, "Enabled case sensitivity for %s" % message_bit)
	
	def case_off(self, request, queryset):
		rows_updated = queryset.update(case_sensitive=False)
		if rows_updated == 1:
			message_bit = "1 word"
		else:
			message_bit = "%s words" % rows_updated
		self.message_user(request, "Disabled case sensitivity for %s" % message_bit)
	
	case_on.short_description = "Mark items case-sensitive"
	case_off.short_description = "Mark items case-insensitive"

class spammers_admin(admin.ModelAdmin):
	search_fields = ['email', 'name', 'notes']
	list_filter = ['timestamp_post', 'timestamp_mod',]
	list_display = ['email', 'name', 'timestamp_post', 'timestamp_mod',]
	readonly_fields = ['timestamp_mod',]
	fieldsets = [
		(None,{'fields':(('email','name',),'notes',),},),
		('Time Options',{'fields':(('timestamp_post','timestamp_mod',),),},),
		('Words Used',{'fields':('word_used',),},),
	]
	actions = ['set_active', 'set_inactive',]
	
	def set_active(self, request, queryset):
		rows_updated = queryset.update(active=True)
		if rows_updated == 1:
			message_bit = "1 sender"
		else:
			message_bit = "%s senders" % rows_updated
		self.message_user(request, "Set %s active" % message_bit)
	
	def set_inactive(self, request, queryset):
		rows_updated = queryset.update(active=False)
		if rows_updated == 1:
			message_bit = "1 sender"
		else:
			message_bit = "%s senders" % rows_updated
		self.message_user(request, "Set %s inactive" % message_bit)
	
	set_active.short_description = "Mark senders active"
	set_inactive.short_description = "Mark senders inactive"

class spam_domain_admin(admin.ModelAdmin):
	search_fields = ['domain', 'notes']
	list_filter = ['manual_entry', 'whitelist', 'timestamp_post', 'timestamp_mod',]
	list_display = ['domain', 'manual_entry', 'whitelist', 'timestamp_post', 'timestamp_mod',]
	readonly_fields = ['timestamp_mod',]
	fieldsets = [
		(None,{'fields':('domain',('whitelist','manual_entry'),'notes',),},),
		('Time Options',{'fields':(('timestamp_post','timestamp_mod',),),},),
	]
	actions = ['set_active', 'set_inactive',]
	
	def set_active(self, request, queryset):
		rows_updated = queryset.update(active=True)
		if rows_updated == 1:
			message_bit = "1 domain"
		else:
			message_bit = "%s domains" % rows_updated
		self.message_user(request, "Set %s active" % message_bit)
	
	def set_inactive(self, request, queryset):
		rows_updated = queryset.update(active=False)
		if rows_updated == 1:
			message_bit = "1 domain"
		else:
			message_bit = "%s domains" % rows_updated
		self.message_user(request, "Set %s inactive" % message_bit)
	
	set_active.short_description = "Mark domains active"
	set_inactive.short_description = "Mark domains inactive"

admin.site.register(link, link_admin)
admin.site.register(contact_link, contact_admin)
admin.site.register(spam_word, spam_admin)
admin.site.register(spam_sender, spammers_admin)
admin.site.register(spam_domain, spam_domain_admin)