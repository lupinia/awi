#	DeerCoins (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from deercoins.models import *

class coins_admin(admin.ModelAdmin):
	list_select_related = True
	list_display = ('code', 'country', 'year', 'currency', 'value', 'is_note', 'is_special_issue', 'acquired_date', 'timestamp_mod', 'timestamp_post')
	list_filter = ['is_note', 'is_special_issue', 'country', 'currency', 'acquired_date', 'timestamp_post', 'timestamp_mod']
	search_fields = ['code', 'coin_notes', 'condition_notes', 'acquired_notes']
	
	class Media:
		js=['js/foldable-list-filter.js',]
		css={'all':['css/foldable-list-filter.css',],}

admin.site.register(coin, coins_admin)
admin.site.register(code_alias)
admin.site.register(currency)
admin.site.register(country)
admin.site.register(euro)