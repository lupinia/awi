#	Awi Access (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Forms
#	=================

import datetime

from django import forms
from django.forms import extras
from django.utils import dateparse
from django.utils import timezone

years_list = sorted(range(timezone.now().year-80, timezone.now().year+1), reverse=True)

class age_verify_form(forms.Form):
	error_css_class = 'has_error';
	
	birthdate = forms.DateField(label='Your Birthdate', widget=extras.SelectDateWidget(years=years_list))
	
	def validate_age(self):
		dob = self.cleaned_data['birthdate']
		cur = timezone.now().date()
		min_age = cur.replace(year=cur.year-18)
		
		if self.cleaned_data['birthdate'] < min_age:
			dob_valid = True
		else:
			dob_valid = False
		
		return dob_valid