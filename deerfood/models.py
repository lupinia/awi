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
from django.utils.encoding import python_2_unicode_compatible

from awi.utils.models import TimestampModel
from awi.utils.text import summarize

@python_2_unicode_compatible
class menu_section(TimestampModel):
	name = models.CharField(max_length=150)
	slug = models.SlugField(unique=True)
	
	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerfood:menu_section', kwargs={'slug':self.slug,})
	
	class Meta:
		verbose_name = 'menu section'


@python_2_unicode_compatible
class menu_flag(TimestampModel):
	name = models.CharField(max_length=250)
	slug = models.SlugField(unique=True)
	img_width = models.IntegerField(null=True, blank=True, verbose_name='icon height')
	img_height = models.IntegerField(null=True, blank=True, verbose_name='icon width')
	icon = models.ImageField(upload_to='menu_icons',height_field='img_height',width_field='img_width')
	
	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerfood:menu_flag', kwargs={'slug':self.slug,})
	
	def get_icon_url(self):
		return "%s%s" % (settings.MEDIA_URL, self.icon.name)
	
	class Meta:
		verbose_name = 'menu item flag'


@python_2_unicode_compatible
class menu_item(TimestampModel):
	name = models.CharField(max_length=150)
	desc = models.TextField(verbose_name='description')
	section = models.ForeignKey(menu_section, on_delete=models.PROTECT)
	flags = models.ManyToManyField(menu_flag, blank=True)
	recipe_internal = models.ForeignKey('deerbooks.page', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='recipe', help_text='Select a Page that contains the recipe for this item.')
	
	def __str__(self):
		return self.name
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.desc, length=length, prefer_long=True)
		else:
			return summarize(body=self.desc, length=length)
	
	@property
	def summary_short(self):
		return self.get_summary()
	
	@property
	def summary_long(self):
		return self.get_summary(512)
	
	# ALIAS
	@property
	def rss_description(self):
		return self.summary_short
	
	class Meta:
		verbose_name = 'menu item'
