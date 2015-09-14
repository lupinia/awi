from django.contrib import admin
from awi_bg.models import background,background_tag

class bg_admin(admin.ModelAdmin):
	list_display=('title','filename','gallery_id')
	list_filter=('tags',)
	
admin.site.register(background,bg_admin)
admin.site.register(background_tag)
