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
		("Options",{'fields':(('auto_export','book_title','book_order',),'showcase_default',('timestamp_revised','revised',),),},),
		('Manage Files',{'fields':('docfiles',),},),
	]
	prepopulated_fields={'slug':('title',)}
	readonly_fields = leaf_admin.readonly_fields + ['timestamp_revised','revised',]
	list_filter = leaf_admin.list_filter + ['book_title','auto_export']
	list_display = ('title','book_title','auto_export',) + leaf_admin.list_display
	filter_horizontal = ['docfiles',] + leaf_admin.filter_horizontal
	
	def view_on_site(self, obj):
		return reverse('page_htm',kwargs={'cached_url':obj.cat.cached_url, 'slug':obj.slug,})
	
	def save_model(self, request, obj, form, change):
		obj.latex_fail = False
		super(page_admin, self).save_model(request, obj, form, change)

class page_inline(admin.TabularInline):
	model = page
	extra = 0
	fields = ['title', 'cat', 'book_order', 'timestamp_post', 'timestamp_mod',]
	readonly_fields = ['timestamp_mod',]


class attachment_admin(admin.ModelAdmin):
	search_fields = ['name','file']
	list_display = ('name','file','timestamp_post','timestamp_mod',)
	list_filter = ['timestamp_post','timestamp_mod',]
	fields = ('name','file','timestamp_post',)


class book_admin(admin.ModelAdmin):
	inlines = [page_inline,]
	fields = (('title', 'slug',),)
	prepopulated_fields={'slug':('title',)}
	search_fields = ['title', 'slug', 'pages__title', 'pages__slug',]
	list_display = ('title', 'slug', 'page_count',)


class docfile_admin(admin.ModelAdmin):
	fields = ('filetype', 'docfile', ('timestamp_mod','page_count',),)
	readonly_fields = ['timestamp_mod','page_count',]
	search_fields = ['docfile', 'pages__title', 'pages__slug',]
	list_display = ('filename', 'filetype', 'page_count', 'timestamp_mod',)
	list_filter = ['filetype','timestamp_mod',]


admin.site.register(page, page_admin)
admin.site.register(toc, book_admin)
admin.site.register(export_file, docfile_admin)
admin.site.register(attachment, attachment_admin)