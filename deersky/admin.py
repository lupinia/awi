#	DeerSky - Digital Almanac and Weather Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin

from deersky.models import city, homepage, secondary_clock

class city_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':('label',('timezone','current_time',),('timezone_order','primary_for_timezone',),),},),
		('Geography', {'fields':(('country','fictional',),('lat','long',),),},),
		('Options', {'fields':('enable_suntime','enable_moon',),},),
		('System', {'fields':(('timestamp_post','timestamp_mod',),),},),
	]
	
	list_filter = ('primary_for_timezone','fictional','enable_suntime','enable_moon','timestamp_post','timestamp_mod',)
	list_display = ('label','timezone_order','fictional','enable_suntime','enable_moon','timestamp_post','timestamp_mod',)
	readonly_fields = ['timestamp_mod','current_time',]
	search_fields = ('name','timezone','country',)

class extraclock_admin(admin.TabularInline):
	model = secondary_clock
	extra = 0
	fields = ['priority', 'city',]

class homepage_admin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':(('title','slug',),'main_city',),},),
		('Backgrounds', {'fields':('backgrounds_override','default_backgrounds',),},),
		('Widgets', {'fields':(('enable_timer','timer_default',),'enable_extraclocks',),},),
		('System', {'fields':(('public','owner',),('timestamp_post','timestamp_mod',),),},),
	]
	
	list_select_related = True
	filter_horizontal = ['backgrounds_override',]
	inlines = [extraclock_admin,]
	list_filter = ('public','enable_timer','enable_extraclocks','owner','timestamp_post','timestamp_mod',)
	list_display = ('slug','main_city','public','timestamp_post','timestamp_mod',)
	readonly_fields = ['timestamp_mod',]
	search_fields = ('title','slug','main_city__label',)

admin.site.register(homepage, homepage_admin)
admin.site.register(city, city_admin)
