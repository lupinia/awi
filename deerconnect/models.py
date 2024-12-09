#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.conf import settings
from django.db import models
from django.utils import timezone

from awi_access.models import access_control
from awi_utils.utils import summarize
from deertrees.models import leaf, category

class link_base(models.Model):
	label = models.CharField(max_length=140)
	url = models.CharField(max_length=250, verbose_name='URL')
	desc = models.TextField(null=True, blank=True, verbose_name='description')
	icon = models.ImageField(upload_to='linkicons', null=True, blank=True)
	icon_large = models.ImageField(upload_to='linkicons_large', null=True, blank=True)
	
	def __unicode__(self):
		return self.label
	
	def get_absolute_url(self):
		return self.url
	
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
	
	@property
	def icon_url(self):
		if self.icon:
			return "%s%s" % (settings.MEDIA_URL,self.icon.name)
		else:
			return "%simages/icons/default-link-16.png" % settings.STATIC_URL
	
	@property
	def icon_large_url(self):
		if self.icon_large:
			return "%s%s" % (settings.MEDIA_URL,self.icon_large.name)
		else:
			return "%simages/icons/default-link-128.png" % settings.STATIC_URL
	
	class Meta:
		abstract = True


class link(link_base, leaf):
	involved = models.BooleanField(help_text="Indicates a project the webmaster has involvement with.")
	healthy = models.BooleanField(default=True, db_index=True, help_text='Indicates whether this link passed its last health check.  Will reset when saved in the admin view.')
	health_check = models.BooleanField(default=True, db_index=True, verbose_name='enable health check?', help_text='Uncheck this to exclude this URL from routine checks to validate that it is still reachable.')


#	This is a special case that won't be part of the usual tree/leaf system, nor will they have tags
#	Instead, these will be displayed on any descendant of a given category
#	To do that, we're bypassing the leaf object, and making these have a unique relationship to their category
class contact_link(link_base, access_control):
	name = models.CharField(max_length=140, verbose_name='username')
	im = models.BooleanField(db_index=True, verbose_name='messaging service?', help_text='Check this box if this link is for an instant-messaging service.')
	
	cat = models.ForeignKey(category, null=True, blank=True, related_name='contact_links', on_delete=models.SET_NULL, verbose_name='category')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def __unicode__(self):
		return '%s - %s' % (self.label, self.name)
	
	def get_absolute_url(self):
		return self.url
	
	@property
	def icon_url(self):
		if self.icon:
			return "%s%s" % (settings.MEDIA_URL, self.icon.name)
		else:
			return "%simages/icons/default-contact-16.png" % settings.STATIC_URL
	
	@property
	def icon_large_url(self):
		if self.icon_large:
			return "%s%s" % (settings.MEDIA_URL, self.icon_large.name)
		else:
			return "%simages/icons/default-contact-128.png" % settings.STATIC_URL
	
	class Meta:
		verbose_name = 'contact link'

#	Keywords to scan for in contact form submissions
class spam_word(models.Model):
	word = models.CharField(max_length=512, unique=True)
	active = models.BooleanField(default=True, blank=True, db_index=True)
	case_sensitive = models.BooleanField(default=False, blank=True, db_index=True)
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	notes = models.TextField(blank=True, null=True)
	
	def __unicode__(self):
		return self.word
	
	class Meta:
		verbose_name = 'spam keyword'

class spam_sender(models.Model):
	email = models.EmailField(max_length=255, unique=True)
	name = models.CharField(max_length=255, null=True, blank=True)
	active = models.BooleanField(default=True, blank=True, db_index=True)
	word_used = models.ManyToManyField(spam_word, blank=True, related_name='used_by')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	notes = models.TextField(blank=True, null=True)
	
	def __unicode__(self):
		return self.email
	
	def save(self, *args, **kwargs):
		from deerconnect.utils import fix_email
		self.email = fix_email(self.email)
		super(spam_sender, self).save(*args, **kwargs)
	
	class Meta:
		verbose_name = 'spam sender'

class spam_domain(models.Model):
	domain = models.CharField(max_length=255, unique=True)
	whitelist = models.BooleanField(default=False, blank=True, db_index=True)
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	notes = models.TextField(blank=True, null=True)
	manual_entry = models.BooleanField(default=False, blank=True, db_index=True)
	
	def __unicode__(self):
		return self.domain
	
	def save(self, *args, **kwargs):
		self.domain = self.domain.lower()
		super(spam_domain, self).save(*args, **kwargs)
	
	class Meta:
		verbose_name = 'spam domain'
