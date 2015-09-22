#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.core.urlresolvers import reverse

from django_summernote.admin import SummernoteModelAdmin
from deertrees.admin import leaf_admin

from deerbooks.models import *

class page_admin(SummernoteModelAdmin,leaf_admin):
	list_select_related = True
	search_fields = ['body','summary','title','slug'] + leaf_admin.search_fields
	fieldsets = [
		(None,{'fields':(('title','slug'),'summary','body'),},),
	] + leaf_admin.fieldsets + [
		("Options",{'fields':(('export','book_title','book_order',),),},),
		('Manage Files',{'fields':('docfiles',),},),
	]
	prepopulated_fields={'slug':('title',)}
	list_filter = leaf_admin.list_filter + ['book_title','timestamp_post','timestamp_mod','export']
	list_display = ('title','cat','book_title','timestamp_post','timestamp_mod','export','published','featured','mature','security',)
	filter_horizontal = ['docfiles',] + leaf_admin.filter_horizontal
	
	#def view_on_site(self, obj):
	#	return reverse('category',kwargs={'cached_url':obj.cached_url,})

admin.site.register(page,page_admin)
admin.site.register(toc)
admin.site.register(export_file)