#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin
from django_summernote.admin import SummernoteModelAdmin
from awi_access.admin import access_admin

from deertrees.models import *

class cat_admin(DjangoMpttAdmin,SummernoteModelAdmin,access_admin):
	list_select_related = True
	fieldsets = [
		(None,{'fields':(('title','slug'),'summary','desc'),},),
		("Options",{'fields':(('parent','background','sitemap_include','content_priority',),),},),
	] + access_admin.fieldsets
	list_filter = access_admin.list_filter + ['background','content_priority','sitemap_include']
	
	list_display = ('title','slug','parent','cached_url')
	prepopulated_fields={'slug':('title',)}
	search_fields = ('title','slug','parent','cached_url','desc')

class tag_admin(SummernoteModelAdmin):
	fieldsets = [
		(None,{'fields':(('title','slug'),'desc'),},),
		("Options",{'fields':(('content_priority','sitemap_include'),),},),
	]

	list_display=('title','slug')
	prepopulated_fields={'slug':('title',)}
	search_fields = ('title','slug')

class leaf_admin(access_admin):
	list_select_related = True
	list_filter = access_admin.list_filter + ['cat',]
	fieldsets = [
		('Time Options',{'fields': (('timestamp_post','timestamp_mod','timedisp'),),},),
		('Categorization',{'fields': ('cat','tags'),},),
	] + access_admin.fieldsets
	
	readonly_fields = ['timestamp_mod',]
	search_fields = ['cat','tags']
	filter_horizontal = ('tags',)

class special_feature_admin(leaf_admin):
	search_fields = ['url','title','desc'] + leaf_admin.search_fields
	fieldsets = [(None,{'fields':(('url','title'),'desc'),},),] + leaf_admin.fieldsets

admin.site.register(category,cat_admin)
admin.site.register(tag,tag_admin)
admin.site.register(special_feature,special_feature_admin)
