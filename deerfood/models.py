#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

class menu_section(models.Model):
	name = models.CharField(max_length=150)
	slug = models.SlugField(unique=True)
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def __unicode__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerfood:menu_section', kwargs={'slug':self.slug,})
	
	class Meta:
		verbose_name = 'menu section'


class menu_flag(models.Model):
	name = models.CharField(max_length=250)
	slug = models.SlugField(unique=True)
	img_width = models.IntegerField(null=True, blank=True, verbose_name='icon height')
	img_height = models.IntegerField(null=True, blank=True, verbose_name='icon width')
	icon = models.ImageField(upload_to='menu_icons',height_field='img_height',width_field='img_width')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	
	def __unicode__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerfood:menu_flag', kwargs={'slug':self.slug,})
	
	def get_icon_url(self):
		return "%s%s" % (settings.MEDIA_URL, self.icon.name)
	
	class Meta:
		verbose_name = 'menu item flag'


class menu_item(models.Model):
	name = models.CharField(max_length=150)
	desc = models.TextField(verbose_name='description')
	section = models.ForeignKey(menu_section, on_delete=models.PROTECT)
	flags = models.ManyToManyField(menu_flag, blank=True)
	recipe_internal = models.ForeignKey('deerbooks.page', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='recipe', help_text='Select a Page that contains the recipe for this item.')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		verbose_name = 'menu item'
