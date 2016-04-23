#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.db import models
from django.conf import settings

from deertrees.models import leaf

class export_file(models.Model):
	FILETYPE_OPTIONS=(('tex','TeX'),('pdf','PDF'),('dvi','DVI'),('ps','PostScript'),('epub','ePub'),)
	
	filetype=models.CharField(max_length=10,choices=FILETYPE_OPTIONS)
	docfile=models.FileField(upload_to='writing')
	timestamp_mod=models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return self.docfile.name
	
	def get_url(self):
		return "%s%s" % (settings.MEDIA_URL,self.docfile.name)

#	Table of Contents
class toc(models.Model):
	title=models.CharField(max_length=60)
	def __unicode__(self):
		return self.title

class page(leaf):
	slug = models.SlugField()
	title = models.CharField(max_length=60)
	body = models.TextField()
	summary = models.CharField(max_length=255,null=True,blank=True)
	
	auto_export = models.BooleanField(default=True,help_text="Uncheck this to disable automatic generation of document files.  Markdown and Plain Text will still be available.")
	docfiles = models.ManyToManyField(export_file,blank=True)
	
	book_title = models.ForeignKey(toc,null=True,blank=True)
	book_order = models.IntegerField(default=0,blank=True)
	
	def get_title(self,raw=False):
		if self.book_title and not raw:
			return "%s:  %s" % (self.book_title.title, self.title)
		else:
			return self.title
	
	def __unicode__(self):
		return self.get_title()
	
	def body_summary(self,length=300):
		if self.summary:
			if len(self.summary) <= length:
				return self.summary
			else:
				return self.summary[:length].rsplit(' ',1)[0]+'...'
		else:
			from django.utils.html import strip_tags
			body_stripped = strip_tags(self.body)
			if len(body_stripped) <= length:
				return body_stripped
			else:
				return body_stripped[:length].rsplit(' ',1)[0]+'...'
