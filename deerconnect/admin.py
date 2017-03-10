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
		(None,{'fields':(('label','involved'),'url','desc','icon'),},),
	] + leaf_admin.fieldsets
	list_filter = leaf_admin.list_filter + ['involved', 'healthy']
	list_display = ('label','url','involved','healthy',) + leaf_admin.list_display
	
	def view_on_site(self, obj):
		return obj.url
	
	def save_model(self, request, obj, form, change):
		obj.healthy = True
		super(link_admin, self).save_model(request, obj, form, change)

class contact_admin(access_admin):
	list_select_related = True
	search_fields = ['label','name','url','desc']
	fieldsets = [
		(None,{'fields':(('label','name','im'),'url','desc','icon','cat'),},),
		('Time Options',{'fields':(('timestamp_post','timestamp_mod',),),},),
	] + access_admin.fieldsets
	list_filter = access_admin.list_filter + ['im',]
	list_display = ('label','name','url','cat','im','timestamp_post','timestamp_mod',) + access_admin.list_display
	readonly_fields = ['timestamp_mod',]
	
	def view_on_site(self, obj):
		return obj.url
	
	def save_model(self, request, obj, form, change):
		obj.healthy = True
		super(contact_admin, self).save_model(request, obj, form, change)

admin.site.register(link,link_admin)
admin.site.register(contact_link,contact_admin)