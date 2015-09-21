#	Awi Error (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	
#	TODO:	Multilingual support
#	=================

from django.db import models

class error(models.Model):
	SEVERITY_OPTIONS=(('critical','Critical (Red)'),('warning','Warning (Orange)'),('notice','Notice (Blue)'))
	
	error_key=models.SlugField()
	severity=models.CharField(max_length=12,choices=SEVERITY_OPTIONS,default='critical')
	message=models.TextField()
	def __unicode__(self):
		return self.error_key
