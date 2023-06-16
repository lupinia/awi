#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	log_list:		Informational display only, for hitlog objects.
#	pointer_admin:	Manage pointers.
#	=================

from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin

from deerfind.models import *

class log_list(admin.TabularInline):
	model=hitlog
	can_delete = False
	extra = 0
	ordering = ('-time',)
	verbose_name_plural = "Recent Hits"
	readonly_fields = ('time', 'referer', 'remote_addr', 'user_agent',)
	fields = ('time', 'referer', 'remote_addr', 'user_agent',)
	
	def has_add_permission(self, request):
		return False

class pointer_admin(admin.ModelAdmin):
	list_display = ('old_url', 'new_url', 'category', 'log_hits', 'hit_count',)
	list_display_links  =  ('old_url',)
	list_filter = ('category', 'log_hits',)
	fields = (('old_url', 'new_url'), ('category', 'log_hits'),)
	list_select_related = True
	ordering = ('new_url',)
	search_fields = ('old_url', 'new_url',)
	inlines = [log_list,]

class g2_admin(admin.ModelAdmin):
	list_select_related = True
	list_display = ('g2id', 'retracted', 'category', 'image', 'asset',)
	ordering = ('g2id',)
	search_fields = ('g2id', 'category__title', 'category__slug',)

class g2_inline(admin.TabularInline):
	model=g2map
	extra=0

class g2raw_admin(DjangoMpttAdmin):
	list_select_related = True


admin.site.register(category)
admin.site.register(pointer,pointer_admin)
admin.site.register(g2map,g2_admin)
admin.site.register(g2raw,g2raw_admin)
