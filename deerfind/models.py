#	DeerFind (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	category:	Purely organizational.
#	pointer:	Maps a known-bad URL to a known-good URL.
#	hitlog:		Tracks basic request information for a hit on a known-bad URL.
#	g2map:		Connects old Gallery2 item IDs with actual URLs in the new system.
#	=================

from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

class category(models.Model):
	title = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.title
	
	class Meta:
		verbose_name = 'pointer type'
		ordering = ['title',]


class pointer(models.Model):
	old_url = models.CharField(max_length=255, unique=True)
	new_url = models.CharField(max_length=255)
	category = models.ForeignKey(category, on_delete=models.PROTECT, verbose_name='type')
	log_hits = models.BooleanField(default=False, blank=True, verbose_name='log hits')
	
	def __unicode__(self):
		return '%s -> %s' % (self.old_url, self.new_url)
	
	@property
	def hit_count(self):
		if self.log_hits:
			return self.hitlog_set.count()
		else:
			return 0
	
	class Meta:
		verbose_name = 'URL redirect pointer'


class hitlog(models.Model):
	pointer = models.ForeignKey(pointer, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now=True)
	
	user_agent = models.TextField(null=True, blank=True)
	accept = models.CharField(max_length=250, null=True, blank=True)
	accept_encoding = models.CharField(max_length=250, null=True, blank=True)
	accept_language = models.CharField(max_length=250, null=True, blank=True)
	
	host = models.CharField(max_length=250, null=True, blank=True)
	referer = models.CharField(max_length=250,null=True, blank=True)
	query_string = models.CharField(max_length=250, null=True, blank=True)
	remote_addr = models.CharField(max_length=250, null=True, blank=True)
	
	@property
	def timestamp_str(self):
		return self.time.strftime('%b %-d, %Y %H:%M:%S')
	
	def __unicode__(self):
		return '%s - %s' % (self.pointer.old_url, self.timestamp_str)
	
	class Meta:
		verbose_name = 'pointer hit log entry'
		verbose_name_plural = 'pointer hit log entries'


class g2map(models.Model):
	g2id = models.IntegerField(unique=True, verbose_name='G2 item ID')
	category = models.ForeignKey('deertrees.category', null=True, blank=True, on_delete=models.SET_NULL)
	image = models.ForeignKey('sunset.image', null=True, blank=True, on_delete=models.SET_NULL)
	
	def __unicode__(self):
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
class g2raw(MPTTModel):
	g2id = models.IntegerField(unique=True, verbose_name='G2 item ID')
	type = models.CharField(max_length=255, default='Unknown')
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
	title = models.CharField(max_length=255, null=True, blank=True)
	matched = models.BooleanField(default=False)
	filename = models.CharField(max_length=255, null=True, blank=True)
	desc = models.TextField(null=True, blank=True)
	creation_timestamp = models.DateTimeField(null=True, blank=True)
	origination_timestamp = models.DateTimeField(null=True, blank=True)
	
	def __unicode__(self):
		return str(self.g2id)
	
	class MPTTMeta:
		order_insertion_by = ['g2id']
	
	class Meta:
		verbose_name = 'legacy Gallery2 item ID'
