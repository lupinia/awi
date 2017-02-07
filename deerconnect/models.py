#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.db import models
from django.utils import timezone

from deertrees.models import leaf, category
from awi_access.models import access_control

class link_base(models.Model):
	label=models.CharField(max_length=140)
	url=models.CharField(max_length=250, verbose_name='URL')
	desc=models.TextField(null=True, blank=True, verbose_name='description')
	icon=models.ImageField(upload_to='linkicons', null=True, blank=True)
	healthy = models.BooleanField(default=True)
	
	class Meta:
		abstract = True

class link(link_base, leaf):
	involved=models.BooleanField(help_text="Indicates a project the webmaster has involvement with.")
	
	def __unicode__(self):
		return self.label

#	This is a special case that won't be part of the usual tree/leaf system, nor will they have tags
#	Instead, these will be displayed on any descendant of a given category
#	To do that, we're bypassing the leaf object, and making these have a unique relationship to their category
class contact_link(link_base, access_control):
	name=models.CharField(max_length=140, verbose_name='username')
	im=models.BooleanField(verbose_name='messaging service?', help_text='Check this box if this link is for an instant-messaging service.')
	
	cat=models.ForeignKey(category, null=True, blank=True, related_name='contact_links', on_delete=models.SET_NULL, verbose_name='category')
	timestamp_mod=models.DateTimeField(auto_now=True, verbose_name='date/time modified')
	timestamp_post=models.DateTimeField(default=timezone.now, verbose_name='date/time created')
	
	def __unicode__(self):
		return '%s - %s' % (self.label, self.name)
	
	class Meta:
		verbose_name = 'contact link'