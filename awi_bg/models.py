#	Awi Background (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	background_tag is how other objects can filter their background options
#	=================

from django.db import models

class background(models.Model):
	filename=models.CharField(max_length=100)
	title=models.CharField(max_length=200)
	gallery_id=models.CharField(max_length=200)
	tags=models.ManyToManyField('background_tag')
	
	def __unicode__(self):
		return self.title
	
class background_tag(models.Model):
	tag=models.CharField(max_length=50)
	def __unicode__(self):
		return self.tag
