#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin Views
#	=================

from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin

from deerfind.models import g2map, g2raw, pointer, category

# Inlines
class g2_inline(admin.TabularInline):
	model=g2map
	extra=0

# Full admin views
class pointer_admin(admin.ModelAdmin):
	list_display = ('old_url', 'new_url', 'category', 'log_hits', 'hit_count',)
	list_display_links  =  ('old_url',)
	list_filter = ('category', 'log_hits',)
	fields = (('old_url', 'new_url'), ('category', 'log_hits'),)
	list_select_related = True
	ordering = ('new_url',)
	search_fields = ('old_url', 'new_url',)

class g2_admin(admin.ModelAdmin):
	list_select_related = True
	list_display = ('g2id', 'retracted', 'category', 'image', 'asset',)
	ordering = ('g2id',)
	search_fields = ('g2id', 'category__title', 'category__slug',)

class g2raw_admin(DjangoMpttAdmin):
	list_select_related = True
	list_display = ('g2id', 'matched', 'type', 'title', 'creation_timestamp', 'origination_timestamp')
	list_filter = ('matched', 'creation_timestamp', 'origination_timestamp', 'type')


admin.site.register(category)
admin.site.register(pointer,pointer_admin)
admin.site.register(g2map,g2_admin)
admin.site.register(g2raw,g2raw_admin)
