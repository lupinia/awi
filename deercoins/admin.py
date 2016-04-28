#	DeerCoins (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin
from deercoins.models import *

admin.site.register(coin)
admin.site.register(code_alias)
admin.site.register(currency)
admin.site.register(country)
admin.site.register(euro)