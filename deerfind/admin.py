from django.contrib import admin
from deerfind.models import *

class log_list(admin.TabularInline):
	model=hitlog
	can_delete = False
	extra = 0
	ordering = ('-time',)
	verbose_name_plural = "Recent Hits"
	readonly_fields = ('time','referer','remote_addr','user_agent')
	fields = ('time','referer','remote_addr','user_agent')
	
	def has_add_permission(self, request):
		return False

class pointer_admin(admin.ModelAdmin):
	list_display = ('old_url','new_url','category','hit_count')
	list_display_links  =  ('old_url',)
	list_filter = ('category',)
	fields = (('old_url','new_url'),'category')
	list_per_page = 20
	list_select_related = True
	ordering = ('new_url',)
	search_fields = ('old_url','new_url')
	inlines = [log_list,]

admin.site.register(category)
admin.site.register(pointer,pointer_admin)