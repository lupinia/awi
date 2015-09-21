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

class cat_admin(DjangoMpttAdmin,SummernoteModelAdmin):
	list_display=('title','slug','parent','cached_url')
	list_filter=('background',)
	fields = (('title','slug'),('parent','background'),'summary','desc')
	prepopulated_fields={'slug':('title',)}
	search_fields = ('title','slug','parent','cached_url','desc')

class tag_admin(SummernoteModelAdmin):
	list_display=('title','slug')
	fields = (('title','slug'),'desc')
	prepopulated_fields={'slug':('title',)}
	search_fields = ('title','slug')

class leaf_admin(access_admin):
	list_select_related = True
	search_fields = ['cat','tags']
	fieldsets = [('Categorization',{'fields': ('cat','tags'),},),] + access_admin.fieldsets
	filter_horizontal = ('tags',)
	list_filter = access_admin.list_filter + ['cat',]

class special_feature_admin(leaf_admin):
	search_fields = ['url','title','desc'] + leaf_admin.search_fields
	fieldsets = [(None,{'fields':(('url','title'),'desc'),},),] + leaf_admin.fieldsets

admin.site.register(category,cat_admin)
admin.site.register(tag,tag_admin)
admin.site.register(special_feature,special_feature_admin)
