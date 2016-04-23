#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.core.urlresolvers import reverse

from django_mptt_admin.admin import DjangoMpttAdmin
from django_summernote.admin import SummernoteModelAdmin
from awi_access.admin import access_admin
from deerfind.admin import g2_inline

from deertrees.models import *

class cat_admin(DjangoMpttAdmin,SummernoteModelAdmin,access_admin):
	list_select_related = True
	fieldsets = [
		(None,{'fields':(('title','slug'),'summary','desc'),},),
		("Options",{'fields':(('parent','background','sitemap_include','content_priority',),),},),
	] + access_admin.fieldsets
	list_filter = access_admin.list_filter + ['background','content_priority','sitemap_include']
	
	list_display = ('title','slug','parent','cached_url','sitemap_include','content_priority','background') + access_admin.list_display
	prepopulated_fields={'slug':('title',)}
	search_fields = ('title','slug','parent','cached_url','desc')
	inlines=[g2_inline,]
	
	def view_on_site(self, obj):
		return reverse('category',kwargs={'cached_url':obj.cached_url,})

class tag_admin(SummernoteModelAdmin):
	fieldsets = [
		(None,{'fields':(('title','slug'),'desc'),},),
		("Options",{'fields':(('content_priority','sitemap_include'),),},),
	]
	
	list_display=('title','slug')
	prepopulated_fields={'slug':('title',)}
	search_fields = ('title','slug')
	
	def view_on_site(self, obj):
		return reverse('tag',kwargs={'slug':obj.slug,})

class leaf_admin(access_admin):
	list_select_related = True
	list_filter = access_admin.list_filter + ['timestamp_post','timestamp_mod','cat','tags',]
	list_display = ('cat','timestamp_post','timestamp_mod',) + access_admin.list_display
	fieldsets = [
		('Time Options',{'fields': (('timestamp_post','timestamp_mod','timedisp'),),},),
		('Categorization',{'fields': ('cat','tags'),},),
	] + access_admin.fieldsets
	
	readonly_fields = ['timestamp_mod',]
	search_fields = ['cat__title','cat__slug','tags__title','tags__slug']
	filter_horizontal = ['tags',]
	actions = ['recycle',] + access_admin.actions
	
	def recycle(self, request, queryset):
		rows_updated = queryset.update(published=False,cat_id=75)
		if rows_updated == 1:
			message_bit = "1 item was"
		else:
			message_bit = "%s items were" % rows_updated
		self.message_user(request, "%s successfully recycled." % message_bit)
	
	recycle.short_description = "Recycle selected items"


class special_feature_admin(leaf_admin):
	search_fields = ['url','title','desc'] + leaf_admin.search_fields
	fieldsets = [(None,{'fields':(('title','url'),'desc'),},),] + leaf_admin.fieldsets
	prepopulated_fields={'url':('title',)}
	list_display = ('title','url') + leaf_admin.list_display
	
	def view_on_site(self, obj):
		return '/' + obj.cat.cached_url + '/' + obj.url

admin.site.register(category,cat_admin)
admin.site.register(tag,tag_admin)
admin.site.register(special_feature,special_feature_admin)
