#	DeerTrees (Django App)
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
from django.utils.html import strip_tags
from django.utils.text import slugify

from datetime import timedelta
from mptt.models import MPTTModel, TreeForeignKey

from awi_utils.utils import format_html, summarize
from awi_access.models import access_control

def viewtype_options():
	blocks_map = settings.DEERTREES_BLOCK_MAP
	viewtypes = []
	for map_name, map in blocks_map.iteritems():
		if map.get('meta',{}).get('option_name',False) and map.get('meta',{}).get('selectable',True):
			viewtypes.append((map_name, map.get('meta',{}).get('option_name',map_name),))
	return viewtypes

class category(MPTTModel, access_control):
	CONTENT_SUMMARY_CHOICES = (
		('misc', 'Miscellaneous'),
		('image', 'Images/Photos'),
		('page', 'Writing'),
		('link', 'External Links'),
	)
	
	title = models.CharField(max_length=60)
	slug = models.SlugField()
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
	summary = models.CharField(max_length=255, null=True, blank=True)
	desc = models.TextField(null=True, blank=True, verbose_name='description body text')
	
	view_type = models.CharField(choices=viewtype_options(), max_length=15, default='default', help_text='Determines the placement of content when this category is displayed.')
	sitemap_include = models.BooleanField(default=True, verbose_name='include in sitemap', help_text='Check this box to include this category in sitemap views.')
	trash = models.BooleanField(default=False, db_index=True, verbose_name='recycle bin', help_text='System field:  Indicates whether this category is the "recycle bin" for deleted items.')
	
	background_tag = models.ForeignKey('sunset.background_tag', null=True, blank=True, on_delete=models.SET_NULL, help_text='Set this to indicate the preferred background image themes for this category.')
	icon = models.ForeignKey('sunset.image_asset', null=True, blank=True, on_delete=models.SET_NULL, help_text='System field:  Image asset used as a thumbnail for this category.')
	icon_manual = models.BooleanField(default=False, db_index=True, help_text='System field:  Indicates whether the Icon field was set manually; if so, it will not be replaced by the automatic thumbnail assignment script.')
	content_summary = models.CharField(max_length=20, default='misc', choices=CONTENT_SUMMARY_CHOICES, help_text='System field:  Stores the main content type for this category, used to display an icon when no image asset is selected.  Will be set by the automatic thumbnail assignment script.')
	
	cached_url = models.CharField(max_length=255, null=True, blank=True, unique=True, help_text='System field:  Full unique slug for this category, including all parents.')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def __unicode__(self):
		return self.title
	
	def get_absolute_url(self):
		return reverse('category', kwargs={'cached_url':self.cached_url,})
	
	@property
	def content_summary_choices_simplified(self):
		choices_simplified = []
		for choice in self.CONTENT_SUMMARY_CHOICES:
			choices_simplified.append(choice[0])
		return choices_simplified
	
	def set_content_summary(self, summary='misc'):
		if summary != self.content_summary:
			choices_simplified = self.content_summary_choices_simplified
			
			if summary in choices_simplified:
				self.content_summary = summary
				self.save()
			else:
				if self.content_summary != 'misc':
					self.content_summary = 'misc'
					self.save()
		
		return self.content_summary
	
	@property
	def body_html(self):
		if self.desc:
			return format_html(self.desc)
		else:
			return format_html(self.summary)
	
	@property
	def icon_url(self):
		if self.icon:
			return self.icon.get_url()
		elif self.mature:
			return "%simages/icons/mature128.png" % settings.STATIC_URL
		else:
			return "%simages/icons/default-category-%s-128.png" % (settings.STATIC_URL, self.content_summary)
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.desc, summary=self.summary, length=length, prefer_long=True)
		else:
			return summarize(body=self.desc, summary=self.summary, length=length)
	
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
	
	def save(self, *args, **kwargs):
		if self.parent:
			self.cached_url = '%s/%s' % (self.parent.cached_url, self.slug)
		else:
			self.cached_url = self.slug
		super(category, self).save(*args, **kwargs)
	
	def can_edit(self, request=False):
		if not request:
			return (False,'access_norequest')
		else:
			canview = self.can_view(request)
			if not canview[0]:
				return canview
			else:
				return super(category, self).can_edit(request, perm_check='deertrees.change_category')
		return (False,'')
	
	class MPTTMeta:
		order_insertion_by = ['title']
	
	class Meta:
		verbose_name_plural = 'categories'

class tag(models.Model):
	title = models.CharField(max_length=200,null=True,blank=True)
	slug = models.SlugField(max_length=200,unique=True)
	desc = models.TextField(null=True,blank=True)
	
	view_type = models.CharField(choices=viewtype_options(), max_length=15, default='default', help_text='Determines the placement of content when this tag is displayed.')
	sitemap_include = models.BooleanField(default=True, verbose_name='include in sitemap', help_text='Check this box to include this tag in sitemap views.')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	@property
	def display_title(self):
		if self.title:
			return self.title
		else:
			return self.slug
	
	def __unicode__(self):
		return self.display_title
	
	def get_absolute_url(self):
		return reverse('tag', kwargs={'slug':self.slug,})
	
	def can_edit(self, request=False):
		if not request:
			return (False,'access_norequest')
		else:
			return (request.user.has_perm('deertrees.change_tag'), 'access_perms')
		return (False,'')
	
	@property
	def synonym_list(self):
		sluglist = []
		if self.title:
			sluglist.append(self.slug)
		
		synonyms = self.synonyms.all().values_list('slug', flat=True)
		if synonyms:
			sluglist += list(synonyms)
		
		return sluglist
	
	@property
	def body_html(self):
		return format_html(self.desc)
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.desc, length=length, prefer_long=True, fallback='')
		else:
			return summarize(body=self.desc, length=length, fallback='')
	
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
		ordering = ['slug',]

class tag_synonym(models.Model):
	parent = models.ForeignKey(tag, on_delete=models.CASCADE, related_name='synonyms')
	slug = models.SlugField(max_length=200,unique=True)
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def get_absolute_url(self):
		return reverse('tag', kwargs={'slug':self.parent.slug,})
	
	def __unicode__(self):
		return self.slug
	
	class Meta:
		ordering = ['slug',]

#	This model has been modified for the Awi website, and requires the Awi Access app
#	This is a single categorized node; everything else that belongs to a category should extend this class
class leaf(access_control):
	TIMEDISP_OPTIONS = (('post','Posted'),('mod','Modified'))
	
	cat = models.ForeignKey(category, null=True, blank=True, on_delete=models.PROTECT, verbose_name='category', related_name='leaves')
	tags = models.ManyToManyField(tag, blank=True, related_name='leaves')
	
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created', help_text='Set this to a future date to schedule it.')
	timedisp = models.CharField(max_length=10, choices=TIMEDISP_OPTIONS, default='post', verbose_name='preferred timestamp', help_text='Determines which timestamp (modified, or created) will be publicly displayed.  The other option will only be visible to users who can edit this item.')
	
	type = models.CharField(max_length=20, default='unknown', db_index=True, help_text='System field:  Indicates which model this leaf is.')
	
	def __unicode__(self):
		return '%s:  %d' % (self.type.capitalize(), self.pk)
	
	def save(self, *args, **kwargs):
		if not self.pk:
			self.type = self.__class__.__name__
		super(leaf, self).save(*args, **kwargs)
	
	def scheduled(self):
		if self.published and self.timestamp_post > timezone.now():
			return True
		else:
			return False
	
	def can_view(self, request=False):
		if not request:
			return (False,'access_norequest')
		
		public_check = self.is_public()
		if public_check[0]:
			return (True, '')
		else:
			canview = super(leaf, self).can_view(request)
			if canview[0] and self.scheduled() and (self.owner != request.user or not request.user.has_perm('deertrees.change_leaf')):
				canview = (False,'access_404')		# If it's scheduled, and we don't have elevated privileges, it doesn't exist.
			
			return canview
	
	def can_edit(self, request=False):
		if not request:
			return (False,'access_norequest')
		else:
			canview = self.can_view(request)
			if not canview[0]:
				return canview
			else:
				return super(leaf, self).can_edit(request, perm_check='deertrees.change_leaf')
		return (False,'')
	
	def is_public(self):
		public, restrictions = super(leaf, self).is_public()
		if self.scheduled():
			public = False
			restrictions.append('Scheduled future postdate')
		
		return (public, restrictions)
	
	# Helper method for extracting a reason for non-public status that's easier to work with programmaticly
	@property
	def restriction(self):
		cur_restriction = super(leaf, self).restriction
		if self.scheduled() and not self.is_public()[0]:
			return 'scheduled'
		else:
			return cur_restriction
	
	def tag_item(self, taglist):
		return_data = {'skipped':[], 'added':[], 'created':[]}
		if ', ' in taglist:
			new_tags = taglist.split(', ')
		elif ',' in taglist:
			new_tags = taglist.split(',')
		else:
			new_tags = [taglist,]
		
		old_tags = {}
		cur_tags = self.tags.all()
		if cur_tags:
			for old_tag in cur_tags:
				old_tags[old_tag.slug] = old_tag
		
		new_tag_objs = []
		for new_tag in new_tags:
			if old_tags.get(new_tag, False):
				return_data['skipped'].append(new_tag)
			else:
				new_tag = slugify(new_tag)
				new_tag_obj = tag.objects.get_or_create(slug=new_tag)
				new_tag_objs.append(new_tag_obj[0])
				if new_tag_obj[1]:
					return_data['created'].append(new_tag)
				else:
					return_data['added'].append(new_tag)
		
		if new_tag_objs:
			self.tags.add(*new_tag_objs)
		
		return return_data
	
	def display_times(self):
		return_times = [{},{}]
		if self.timedisp == 'post':
			return_mod = 1
			return_post = 0
		else:
			return_mod = 0
			return_post = 1
		
		return_times[return_post]['timestamp'] = self.timestamp_post
		return_times[return_mod]['timestamp'] = self.timestamp_mod
		return_times[return_post]['label'] = 'Posted'
		return_times[return_mod]['label'] = 'Updated'
		
		return return_times
	
	@property
	def timestamp(self):
		if self.timedisp == 'post':
			return self.timestamp_post
		else:
			return self.timestamp_mod
	
	@property
	def rss_description(self):
		return 'No Description'
	
	@property
	def is_recent(self):
		if self.timestamp > (timezone.now() - timedelta(days=30*6)):
			return True
		else:
			return False


#	Create a leaf that links to something else that isn't part of this category system.
#	Handy for things like third-party apps, or self-contained apps with their own organizational structure.
class special_feature(leaf):
	url = models.CharField(max_length=60, unique=True, verbose_name='URL', help_text='Similar to a Slug field, but can accept any character, to make it easier to link to non-DeerTrees URLs.')
	title = models.CharField(max_length=60)
	desc = models.CharField(max_length=255, null=True, blank=True, verbose_name='Description')
	
	def get_absolute_url(self):
		return '%s%s' % (reverse('category', kwargs={'cached_url':self.cat.cached_url,}), self.url)
	
	def __unicode__(self):
		return self.title
	
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
		verbose_name = 'special feature'
