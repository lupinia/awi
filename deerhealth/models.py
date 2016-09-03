#	DeerHealth (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from datetime import date,timedelta
from django.db import models
from django.contrib.auth.models import User

class prescription(models.Model):
	name=models.CharField(max_length=150)
	fullname=models.CharField(max_length=150, blank=True, null=True)
	slug=models.SlugField()
	quantity=models.IntegerField(help_text="The amount that you have right now, minus today's dose")
	per_day=models.IntegerField(help_text="The total number of these you take per day")
	last_update=models.DateField(auto_now=True)
	owner=models.ForeignKey(User)
	
	def __unicode__(self):
		return self.name
	
	#	Get the number of pills remaining
	def remaining(self):
		if date.today() == self.last_update or not self.per_day:
			pills_remaining = self.quantity
		else:
			days_since_update=date.today() - self.last_update
			days_since_update=days_since_update.days
			pills_used=days_since_update * self.per_day
			pills_remaining=self.quantity - pills_used
		return pills_remaining
	
	#	Get the date when they'll run out
	@property
	def end_date(self):
		if self.per_day:
			pills_remaining=self.remaining()
			days_remaining = pills_remaining / self.per_day
			end_date=date.today() + timedelta(days=days_remaining)
		else:
			end_date='N/A'
		return end_date
