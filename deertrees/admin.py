#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from django.contrib.messages import constants as messages
from django.core.urlresolvers import reverse

from django_mptt_admin.admin import DjangoMpttAdmin
from awi_access.admin import access_admin
from deerfind.admin import g2_inline

from deertrees.models import category, tag, tag_synonym, external_link, external_link_type, special_feature

class external_link_type_admin(admin.ModelAdmin):
	list_select_related = True
	fieldsets = [
		(None, {'fields':(('name', 'label',), 'url_format', 'icon', 'notes'),},),
		("Options", {'fields':(('featured', 'public',), 'sites',),},),
	]
	search_fields = ('name', 'label', 'notes', 'url_format',)
	list_display = ('name', 'public', 'featured',)
	list_filter = ['public', 'featured',]

class external_link_admin(admin.ModelAdmin):
	list_select_related = True
	fieldsets = [
		(None, {'fields':('full_url', 'remote_id', 'parent', 'notes'),},),
		("Options", {'fields':(('link_type', 'label_override',), ('published', 'automated',), ('timestamp_post', 'timestamp_mod',), ),},),
	]
	readonly_fields = ['timestamp_mod','automated',]
	search_fields = ('full_url', 'remote_id', 'notes',)
	list_display = ('link_type', 'parent', 'url', 'published',)
	list_filter = ['link_type', 'published', 'link_type__public', 'link_type__featured',]

class ext_link_inline(admin.TabularInline):
	model = external_link
	extra = 0
	fields = ['link_type', 'full_url', 'remote_id', 'published', 'timestamp_post', 'timestamp_mod',]
	readonly_fields = ['timestamp_mod',]

class cat_admin(DjangoMpttAdmin,access_admin):
	list_select_related = True
	fieldsets = [
		(None,{'fields':(('title', 'slug',), 'parent', 'summary', 'desc'),},),
		("Options",{'fields':(('view_type', 'background_tag',), ('sitemap_include','always_fresh','trash',),),},),
		('Time Options',{'fields': (('timestamp_post','timestamp_mod',),),},),
	] + access_admin.fieldsets
	list_filter = access_admin.list_filter + ['background_tag', 'view_type', 'sitemap_include']
	
	list_display = ('title', 'slug', 'parent', 'cached_url', 'sitemap_include', 'view_type', 'background_tag') + access_admin.list_display
	prepopulated_fields={'slug':('title',)}
	readonly_fields = ['timestamp_mod',]
	search_fields = ('title','slug','parent','cached_url','desc')
	inlines=[g2_inline,]
	
	def view_on_site(self, obj):
		return reverse('category',kwargs={'cached_url':obj.cached_url,})

class synonym_inline(admin.TabularInline):
	model = tag_synonym
	extra = 0
	fields = ['slug', 'timestamp_post', 'timestamp_mod',]
	readonly_fields = ['timestamp_mod',]

class tag_admin(admin.ModelAdmin):
	fieldsets = [
		(None,{'fields':(('title','slug'),'desc'),},),
		("Options",{'fields':(('public','sitemap_include'),'view_type',),},),
		('Time Options',{'fields': (('timestamp_post','timestamp_mod',),),},),
	]
	list_filter = ['public', 'sitemap_include', 'timestamp_post', 'timestamp_mod',]
	
	list_display=('display_title', 'slug', 'public', 'sitemap_include', 'timestamp_post', 'timestamp_mod',)
	prepopulated_fields={'slug':('title',)}
	readonly_fields = ['timestamp_mod',]
	search_fields = ('title','slug','desc',)
	inlines = [synonym_inline,]
	
	def view_on_site(self, obj):
		return reverse('tag',kwargs={'slug':obj.slug,})

class leaf_admin(access_admin):
	list_select_related = True
	list_filter = access_admin.list_filter + ['timestamp_post','timestamp_mod','cat','tags',]
	list_display = ('cat','timestamp_post','timestamp_mod',) + access_admin.list_display
	fieldsets = [
		('Additional Settings',{'fields': ('author_override',),},),
		('Time Options',{'fields': (('timestamp_post','timestamp_mod','timedisp'),),},),
		('Categorization',{'fields': ('cat','tags'),},),
	] + access_admin.fieldsets
	
	readonly_fields = ['timestamp_mod',]
	search_fields = ['cat__title','cat__slug','tags__title','tags__slug']
	filter_horizontal = ['tags',]
	actions = ['recycle',] + access_admin.actions
	inlines = [ext_link_inline,]
	
	def recycle(self, request, queryset):
		recycle_bin = category.objects.filter(trash=True).first()
		if recycle_bin:
			rows_updated = queryset.update(published=False,cat=recycle_bin)
			if rows_updated == 1:
				message_bit = "1 item was"
			else:
				message_bit = "%s items were" % rows_updated
			self.message_user(request, "%s successfully recycled." % message_bit)
		else:
			self.message_user(request, "Cannot recycle items until a recycle bin category is defined.", level=messages.ERROR)
	
	recycle.short_description = "Recycle selected items"


class special_feature_admin(leaf_admin):
	search_fields = ['url','title','desc'] + leaf_admin.search_fields
	fieldsets = [(None,{'fields':(('title','directory',),('url','url_reverse',),'desc'),},),] + leaf_admin.fieldsets
	prepopulated_fields={'url':('title',)}
	list_display = ('title','url','emulation_mode') + leaf_admin.list_display
	
	def view_on_site(self, obj):
		return '/' + obj.cat.cached_url + '/' + obj.url

admin.site.register(category,cat_admin)
admin.site.register(tag,tag_admin)
admin.site.register(special_feature,special_feature_admin)
admin.site.register(external_link_type,external_link_type_admin)
admin.site.register(external_link,external_link_admin)
