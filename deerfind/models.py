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

class category(models.Model):
	title = models.CharField(max_length = 200)
	
	def __unicode__(self):
		return self.title
	
class pointer(models.Model):
	old_url = models.CharField(max_length = 200, unique=True)
	new_url = models.CharField(max_length = 200)
	category = models.ForeignKey(category, on_delete=models.PROTECT)
	
	def __unicode__(self):
		return '%s -> %s' % (self.old_url,self.new_url)
	
	def hit_count(self):
		return self.hitlog_set.count()

class hitlog(models.Model):
	pointer = models.ForeignKey(pointer, on_delete=models.CASCADE)
	time=models.DateTimeField(auto_now=True)

	user_agent = models.TextField(null = True,blank = True)
	accept = models.CharField(max_length = 250,null = True,blank = True)
	accept_encoding = models.CharField(max_length = 250,null = True,blank = True)
	accept_language = models.CharField(max_length = 250,null = True,blank = True)

	host = models.CharField(max_length = 250,null = True,blank = True)
	referer = models.CharField(max_length = 250,null = True,blank = True)
	query_string = models.CharField(max_length = 250,null = True,blank = True)
	remote_addr = models.CharField(max_length = 250,null = True,blank = True)
	
	def __unicode__(self):
		hit_date = self.time.strftime('%b %-d, %Y %H:%M:%S')
		return '%s - %s' % (self.pointer.old_url,hit_date)

class g2map(models.Model):
	g2id = models.IntegerField(unique=True)
	category = models.ForeignKey('deertrees.category', null=True, blank=True)
	image = models.ForeignKey('sunset.image', null=True, blank=True)
	
	def __unicode__(self):
		return str(self.g2id)
