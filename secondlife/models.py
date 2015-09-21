#	secondlife (Legacy Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.db import models

class security_control(models.Model):
	GRID_OPTIONS=(('sl','Second Life'),('opensim_lup','OpenSim (Lupinia)'))
	
	name=models.CharField(max_length=150)
	key=models.CharField(max_length=255)
	auth=models.BooleanField()
	grid=models.CharField(max_length=20,choices=GRID_OPTIONS,default='sl')
	def __unicode__(self):
		return self.name
