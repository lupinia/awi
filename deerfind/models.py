#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	category:	Purely organizational.
#	pointer:	Maps a known-bad URL to a known-good URL.
#	g2map:		Connects old Gallery2 item IDs with actual URLs in the new system.
#	=================

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from mptt.models import MPTTModel, TreeForeignKey

from sunset.models import image_asset_type_choices

@python_2_unicode_compatible
class category(models.Model):
	title = models.CharField(max_length=200)
	
	def __str__(self):
		return self.title
	
	class Meta:
		verbose_name = 'pointer type'
		ordering = ['title',]


@python_2_unicode_compatible
class pointer(models.Model):
	old_url = models.CharField(max_length=255, unique=True)
	new_url = models.CharField(max_length=255)
	category = models.ForeignKey(category, on_delete=models.PROTECT, verbose_name='type')
	log_hits = models.BooleanField(default=False, blank=True, verbose_name='log hits')
	
	def __str__(self):
		return '%s -> %s' % (self.old_url, self.new_url)
	
	@property
	def hit_count(self):
		if self.log_hits:
			return 0
		else:
			return 0
	
	class Meta:
		verbose_name = 'URL redirect pointer'


@python_2_unicode_compatible
class g2map(models.Model):
	g2id = models.IntegerField(unique=True, verbose_name='G2 item ID')
	category = models.ForeignKey('deertrees.category', null=True, blank=True, on_delete=models.SET_NULL)
	image = models.ForeignKey('sunset.image', null=True, blank=True, on_delete=models.SET_NULL)
	asset = models.CharField(max_length=16, null=True, blank=True, choices=image_asset_type_choices())
	
	def __str__(self):
		return str(self.g2id)
	
	@property
	def retracted(self):
		if not self.category and not self.image:
			return True
		else:
			return False
	
	@property
	def dest_type(self):
		if self.image:
			return 'image'
		elif self.category:
			return 'category'
		else:
			return 'retracted'
	
	class Meta:
		verbose_name = 'Gallery2 URL redirect pointer'

# Temporary object for managing the migration from Gallery2 to Sunset
@python_2_unicode_compatible
class g2raw(MPTTModel):
	g2id = models.IntegerField(unique=True, verbose_name='G2 item ID')
	type = models.CharField(max_length=255, default='Unknown', db_index=True)
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
	title = models.CharField(max_length=255, null=True, blank=True)
	matched = models.BooleanField(default=False, db_index=True)
	filename = models.CharField(max_length=255, null=True, blank=True)
	
	desc = models.TextField(null=True, blank=True)
	summary = models.TextField(null=True, blank=True)
	owner_id = models.IntegerField(default=0, blank=True)
	creation_timestamp = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='upload time')
	origination_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='capture time')
	asset = models.CharField(max_length=16, null=True, blank=True, choices=image_asset_type_choices())
	derivative_type = models.IntegerField(default=-1, blank=True)
	derivative_ops = models.TextField(null=True, blank=True)
	derivative_params = models.TextField(null=True, blank=True)
	derivative_width = models.IntegerField(default=0, blank=True)
	derivative_height = models.IntegerField(default=0, blank=True)
	
	def __str__(self):
		return str(self.g2id)
	
	class MPTTMeta:
		order_insertion_by = ['g2id']
	
	class Meta:
		verbose_name = 'legacy Gallery2 item ID'
