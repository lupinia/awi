#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from deerbooks.models import page

class menu_section(models.Model):
	name=models.CharField(max_length=150)
	slug=models.SlugField(unique=True)
	timestamp_mod=models.DateTimeField(auto_now=True)
	timestamp_post=models.DateTimeField(default=timezone.now)
	def __unicode__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerfood:menu_section', kwargs={'slug':self.slug,})

class menu_flag(models.Model):
	name=models.CharField(max_length=250)
	slug=models.SlugField(unique=True)
	img_width=models.IntegerField(null=True,blank=True)
	img_height=models.IntegerField(null=True,blank=True)
	icon=models.ImageField(upload_to='menu_icons',height_field='img_height',width_field='img_width')
	def __unicode__(self):
		return self.name

class menu_item(models.Model):
	name=models.CharField(max_length=150)
	desc=models.TextField()
	section=models.ForeignKey(menu_section)
	flags=models.ManyToManyField(menu_flag,blank=True)
	recipe_internal=models.ForeignKey(page,null=True,blank=True)
	timestamp_mod=models.DateTimeField(auto_now=True)
	timestamp_post=models.DateTimeField(default=timezone.now)
	def __unicode__(self):
		return self.name