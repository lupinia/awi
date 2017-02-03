#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.core.urlresolvers import reverse

from deertrees.admin import leaf_admin

from deerbooks.models import *

class page_admin(leaf_admin):
	list_select_related = True
	search_fields = ['body','summary','title','slug'] + leaf_admin.search_fields
	fieldsets = [
		(None,{'fields':(('title','slug'),'summary','body'),},),
	] + leaf_admin.fieldsets + [
		("Options",{'fields':(('auto_export','book_title','book_order',),),},),
		('Manage Files',{'fields':('docfiles',),},),
	]
	prepopulated_fields={'slug':('title',)}
	list_filter = leaf_admin.list_filter + ['book_title','auto_export']
	list_display = ('title','book_title','auto_export',) + leaf_admin.list_display
	filter_horizontal = ['docfiles',] + leaf_admin.filter_horizontal
	
	def view_on_site(self, obj):
		return reverse('page_htm',kwargs={'cached_url':obj.cat.cached_url, 'slug':obj.slug,})


class attachment_admin(admin.ModelAdmin):
	search_fields = ['name','file']
	list_display = ('name','file','timestamp_post','timestamp_mod',)
	list_filter = ['timestamp_post','timestamp_mod',]
	fields = ('name','file','timestamp_post',)


admin.site.register(page,page_admin)
admin.site.register(toc)
admin.site.register(export_file)
admin.site.register(attachment, attachment_admin)