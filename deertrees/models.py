#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from mptt.models import MPTTModel, TreeForeignKey
from awi_access.models import access_control

class category(MPTTModel, access_control):
	PRIORITY_OPTIONS = (('image','Photos'),('page','Writing'),('desc','Category Description'),)
	
	title=models.CharField(max_length=60)
	slug=models.SlugField()
	summary=models.CharField(max_length=255)
	desc=models.TextField(null=True,blank=True)
	parent=TreeForeignKey('self',null=True,blank=True,related_name='children')
	cached_url=models.CharField(max_length=255,null=True,blank=True,unique=True)
	
	background_tag=models.ForeignKey('sunset.background_tag',null=True,blank=True)
	content_priority=models.CharField(choices=PRIORITY_OPTIONS,max_length=10,null=True,blank=True,help_text="Manually specify a content type to prioritize during display.")		#	An option to override the content given top priority
	sitemap_include=models.BooleanField(default=True)
	timestamp_mod=models.DateTimeField(auto_now=True)
	timestamp_post=models.DateTimeField(default=timezone.now)
	
	def __unicode__(self):
		return self.title
	
	def get_absolute_url(self):
		return reverse('category', kwargs={'cached_url':self.cached_url,})
	
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
	slug=models.SlugField(max_length=200,unique=True)
	desc=models.TextField(null=True,blank=True)
	
	content_priority=models.CharField(choices=PRIORITY_OPTIONS,max_length=10,null=True,blank=True)		#	An option to override the content given top priority
	sitemap_include=models.BooleanField(default=True)
	timestamp_mod=models.DateTimeField(auto_now=True)
	timestamp_post=models.DateTimeField(default=timezone.now)
	
	def __unicode__(self):
		if self.title:
			return self.title
		else:
			return self.slug
	
	def get_absolute_url(self):
		return reverse('tag', kwargs={'slug':self.slug,})
	
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
		ispublic = super(leaf, self).is_public()
		if self.scheduled():
			ispublic[0] = False
			ispublic[1].append('Scheduled future postdate')
		
		return ispublic
	
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
	
	def get_absolute_url(self):
		return '%s%s' % (reverse('category', kwargs={'cached_url':self.cat.cached_url,}), self.url)
	
	def __unicode__(self):
		return self.title
