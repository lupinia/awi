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
from django.utils.encoding import python_2_unicode_compatible

from awi_access.models import access_control
from awi.utils.text import summarize
from deertrees.models import leaf, category

@python_2_unicode_compatible
class link_base(models.Model):
	label = models.CharField(max_length=140)
	url = models.CharField(max_length=250, verbose_name='URL')
	desc = models.TextField(null=True, blank=True, verbose_name='description')
	icon = models.ImageField(upload_to='linkicons', null=True, blank=True)
	icon_large = models.ImageField(upload_to='linkicons_large', null=True, blank=True)
	
	def __str__(self):
		return self.label
	
	def get_absolute_url(self):
		return self.url
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.desc, length=length, prefer_long=True)
		else:
			return summarize(body=self.desc, length=length)
	
	@property
	def url_domain_name(self):
		dname = self.url.replace('www.', '')
		if '://' in dname:
			discard, dname = dname.split('://')
		
		if '/' in dname:
			name_pieces = dname.split('/')
			dname = name_pieces[0]
		
		return dname
	
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
	
	def __str__(self):
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


#	Spam filtering
merge_note_delimiter = '\n=======\n'

#	Keywords to scan for in contact form submissions
@python_2_unicode_compatible
class spam_word(models.Model):
	TYPE_CHOICES = (
		('keyword','Keyword'),
		('domain','Domain Name'),
		('url','Full URL'),
		('contact','Contact Info'),
		('name','Org Name'),
	)
	
	word = models.CharField(max_length=512, unique=True)
	wordtype = models.CharField(max_length=32, choices=TYPE_CHOICES, default='keyword', verbose_name='type', db_index=True)
	active = models.BooleanField(default=True, blank=True, db_index=True)
	case_sensitive = models.BooleanField(default=False, blank=True, db_index=True)
	notes = models.TextField(blank=True, null=True)
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	used_count = models.PositiveSmallIntegerField(default=0, blank=True, verbose_name='used')
	merged = models.BooleanField(default=False, blank=True, verbose_name='has been merged')
	
	def __str__(self):
		return '%s: %s' % (self.get_wordtype_display(), self.word)
	
	def update_used_count(self):
		"""Recalculate the cached value for used_count based on number of spam_senders referencing this word."""
		spam_word.objects.filter(pk=self.pk).update(used_count=self.used_by.all().count())
	
	def split_notes(self):
		"""
		Retrieve the main notes body and merge history separately.
		Returns two values, both strings:
			notes_body:		The main body text of the notes field, if any
			merge_history:	A newline-separated block of merge actions, if any
		"""
		notes_body = ''
		merge_history = ''
		if self.merged and 'spam_word.merge():' in self.notes:
			if merge_note_delimiter in self.notes:
				# There's actually something to split!
				noteparts = self.notes.rsplit(merge_note_delimiter, 2)
				if 'spam_word.merge():' in noteparts[1]:
					notes_body, merge_history = noteparts
				else:
					# Nevermind, apparently it's a false alarm
					notes_body = self.notes
			
			elif 'spam_word.merge():' in self.notes:
				# No previous notes, just the merge history
				merge_history = self.notes
			
		elif self.notes:
			notes_body = self.notes
		
		return (notes_body, merge_history)
	
	def merge(self, target):
		"""
		spam_word.merge(target) -> (success, reason)
		Merge target spam_word into this spam_word, keeping all relationships for both.
		Target object's case_sensitive setting will be discarded
		Notes fields will be merged, and an additional note regarding the merge added.
		Active will be set to True if either word is set active. 
		Oldest timestamp_post value will be kept.
		Only this spam_word's value for word will be kept, intended use is to simplify overlaps.
			Example: Merge 'a better solution to manage SEO' with 'manage SEO'
		NOTE:  Object provided as target parameter will be deleted!
		
		Returns a tuple:
			success: Boolean, indicates whether the merge succeeded
			reason:  String, provides a reason for failure if success is False
		"""
		success = False
		reason = ''
		if type(self) != type(target):
			success = False
			reason = 'object type mismatch'
		else:
			target_older = False
			if target.timestamp_post < self.timestamp_post:
				# Use the oldest timestamp
				self.timestamp_post = target.timestamp_post
				target_older = True
			
			# Preparing to add notes indicating our actions here
			cur_time = timezone.now().strftime('%x %X')
			merge_history = ''
			my_notes, my_history = self.split_notes()
			target_notes, target_history = target.split_notes()
			
			if my_notes and target_notes:
				if target_older:
					my_notes = '%s\n---\n%s\n' % (target_notes, my_notes)
				else:
					my_notes = '%s\n---\n%s\n' % (my_notes, target_notes)
			elif target_notes:
				my_notes = target_notes
			
			if my_notes:
				my_notes = '%s%s' % (my_notes, merge_note_delimiter)
			
			if my_history and target_history:
				if target_older:
					my_history = '%s\n%s' % (target_history, my_history)
				else:
					my_history = '%s\n%s' % (my_history, target_history)
			elif target_history:
				my_history = target_history
			
			if my_history:
				my_history = '%s\n' % my_history
			
			self.notes = '%s%sspam_word.merge(): Merged %d (%s): %s' % (my_notes, my_history, target.pk, target.word, cur_time)
			
			# Moving affiliated spam senders
			# I don't love that the only way to do this is a loop
			target_senders = target.used_by.all()
			for sender in target_senders:
				sender.word_used.add(self)
			
			# Looks like we're all set!  Let's do this!
			self.merged = True
			self.save()
			target.delete()
			self.update_used_count()
			success = True
		
		return (success, reason)
	
	class Meta:
		verbose_name = 'spam keyword'

@python_2_unicode_compatible
class spam_sender(models.Model):
	email = models.EmailField(max_length=255, unique=True)
	name = models.CharField(max_length=255, null=True, blank=True)
	active = models.BooleanField(default=True, blank=True, db_index=True)
	word_used = models.ManyToManyField(spam_word, blank=True, related_name='used_by')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	notes = models.TextField(blank=True, null=True)
	
	def __str__(self):
		return self.email
	
	def save(self, *args, **kwargs):
		from deerconnect.utils import fix_email
		self.email = fix_email(self.email)
		super(spam_sender, self).save(*args, **kwargs)
	
	class Meta:
		verbose_name = 'spam sender'

@python_2_unicode_compatible
class spam_domain(models.Model):
	domain = models.CharField(max_length=255, unique=True)
	whitelist = models.BooleanField(default=False, blank=True, db_index=True)
	active = models.BooleanField(default=True, blank=True, db_index=True)
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	notes = models.TextField(blank=True, null=True)
	manual_entry = models.BooleanField(default=False, blank=True, db_index=True)
	
	def __str__(self):
		return self.domain
	
	def save(self, *args, **kwargs):
		self.domain = self.domain.lower()
		super(spam_domain, self).save(*args, **kwargs)
	
	class Meta:
		verbose_name = 'spam domain'
