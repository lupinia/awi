from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
#from model_utils.managers import InheritanceManager

from awi_access.models import access_control

class category(MPTTModel):
	title=models.CharField(max_length=60)
	slug=models.SlugField()
	desc=models.TextField(null=True,blank=True)
	parent=TreeForeignKey('self',null=True,blank=True,related_name='children')
	cached_url=models.CharField(max_length=255,null=True,blank=True)
	background=models.ForeignKey('awi_bg.background_tag',null=True,blank=True)
	
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
	title=models.CharField(max_length=200,null=True,blank=True)
	slug=models.SlugField(max_length=200)
	desc=models.TextField(null=True,blank=True)
	
	def __unicode__(self):
		if self.title:
			return self.title
		else:
			return self.slug

class leaf(models.Model):
	cat=models.ForeignKey(category,null=True,blank=True)
	tags=models.ManyToManyField(tag,null=True,blank=True)
#	nodes=InheritanceManager()
	
	def __unicode__(self):
		return str(self.id)

#	This model has been modified for the Awi website, and requires the Awi Access app
class special_feature(leaf, access_control):
	url=models.CharField(max_length=60,unique=True)
	title=models.CharField(max_length=60)
	desc=models.TextField(null=True,blank=True)
	
	def __unicode__(self):
		return self.title
