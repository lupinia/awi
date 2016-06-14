#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.db import models
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey
from awi_access.models import access_control

class category(MPTTModel, access_control):
	PRIORITY_OPTIONS = (('photo','Photos'),('page','Writing'),('desc','Category Description'),)
	
	title=models.CharField(max_length=60)
	slug=models.SlugField()
	summary=models.CharField(max_length=255)
	desc=models.TextField(null=True,blank=True)
	parent=TreeForeignKey('self',null=True,blank=True,related_name='children')
	cached_url=models.CharField(max_length=255,null=True,blank=True)
	
	background=models.ForeignKey('awi_bg.background_tag',null=True,blank=True)
	content_priority=models.CharField(choices=PRIORITY_OPTIONS,max_length=10,null=True,blank=True,help_text="Manually specify a content type to prioritize during display.")		#	An option to override the content given top priority
	sitemap_include=models.BooleanField(default=True)
	
	def __unicode__(self):
		return self.title
		
	def save(self, *args, **kwargs):
		if self.parent:
			self.cached_url = '%s/%s' % (self.parent.cached_url, self.slug)
		else:
			self.cached_url = self.slug
		super(category, self).save(*args, **kwargs)
	
	class MPTTMeta:
		order_insertion_by = ['title']

class tag(models.Model):
	PRIORITY_OPTIONS = (('photo','Photos'),('page','Writing'),('desc','Category Description'),)
	
	title=models.CharField(max_length=200,null=True,blank=True)
	slug=models.SlugField(max_length=200)
	desc=models.TextField(null=True,blank=True)
	
	content_priority=models.CharField(choices=PRIORITY_OPTIONS,max_length=10,null=True,blank=True)		#	An option to override the content given top priority
	sitemap_include=models.BooleanField(default=True)
	
	def __unicode__(self):
		if self.title:
			return self.title
		else:
			return self.slug
	
	class Meta:
		ordering = ['slug',]

#	This model has been modified for the Awi website, and requires the Awi Access app
#	This is a single categorized node; everything else that belongs to a category should extend this class
class leaf(access_control):
	TIMEDISP_OPTIONS=(('post','Posted'),('mod','Modified'))
	
	cat=models.ForeignKey(category,null=True,blank=True)
	tags=models.ManyToManyField(tag,blank=True)
	
	timestamp_mod=models.DateTimeField(auto_now=True)
	timestamp_post=models.DateTimeField(default=timezone.now)
	timedisp=models.CharField(max_length=10,choices=TIMEDISP_OPTIONS,default='post')
	
	def __unicode__(self):
		return str(self.id)
	
	def scheduled(self):
		if self.published and self.timestamp_post > timezone.now():
			return True
		else:
			return False
	
	def can_view(self, request=False):
		canview = super(leaf, self).can_view(request)
		
		if canview[0]:
			if self.scheduled():
				if not request:
					canview = (False,'')
				if not request.user.is_authenticated() or (not request.user.is_staff and self.owner != request.user):
					canview = (False,'access_404')
		
		return canview
	
	def display_times(self):
		return_times=[{},{}]
		if self.timedisp=='post':
			return_mod=1
			return_post=0
		else:
			return_mod=0
			return_post=1
		
		return_times[return_post]['timestamp']=self.timestamp_post
		return_times[return_mod]['timestamp']=self.timestamp_mod
		return_times[return_post]['label']='Posted'
		return_times[return_mod]['label']='Updated'
		
		return return_times
		

#	Create a leaf that links to something else that isn't part of this category system.
#	Handy for things like third-party apps, or self-contained apps with their own organizational structure.
class special_feature(leaf):
	url=models.CharField(max_length=60,unique=True)
	title=models.CharField(max_length=60)
	desc=models.CharField(max_length=255,null=True,blank=True)
	
	def __unicode__(self):
		return self.title
