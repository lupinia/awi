#	Election Map - Electoral Data Visualization (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Admin
#	=================

from django.contrib import admin

from electionmap.models import (
	state,
	election,
	election_seats,
	data_source,
	results_house,
	results_senate,
	results_president,
)

admin.site.register(state)
admin.site.register(election)
admin.site.register(election_seats)
admin.site.register(data_source)
admin.site.register(results_house)
admin.site.register(results_senate)
admin.site.register(results_president)
