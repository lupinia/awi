#	secondlife (Legacy Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.db import models
from django.utils.safestring import mark_safe

class security_control(models.Model):
	GRID_OPTIONS = (('sl','Second Life'),('opensim_lup','OpenSim (Lupinia)'))
	
	name = models.CharField(max_length=150, help_text=mark_safe('The <a href="http://wiki.secondlife.com/wiki/Category:LSL_Avatar/Name" target="_BLANK">legacy name</a> of this user.'))
	key = models.CharField(max_length=255, unique=True, help_text=mark_safe('The unique identifier for this user.  <a href="http://wiki.secondlife.com/wiki/Category:LSL_Key" target="_BLANK">More info</a>.'))
	auth = models.BooleanField(verbose_name='authorized?', help_text='Check this box to allow this user access to in-world secure systems/areas.')
	grid = models.CharField(max_length=20, choices=GRID_OPTIONS, default='sl', help_text='Select the virtual world/"grid" for this user.')
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		verbose_name = 'authorized user'
