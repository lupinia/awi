#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from deertrees.models import leaf

class export_file(models.Model):
	FILETYPE_OPTIONS=(
		('tex','TeX'),
		('pdf','PDF'),
		('dvi','DVI'),
		('ps','PostScript'),
		('epub','ePub'),
		('txt','Plain Text'),
		('md','Markdown'),
		('rtf','Rich Text (RTF)'),
		('docx','Word Document (DocX)'),
	)
	
	filetype=models.CharField(max_length=10,choices=FILETYPE_OPTIONS)
	docfile=models.FileField(upload_to='writing')
	timestamp_mod=models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return self.docfile.name
	
	def get_url(self):
		return "%s%s" % (settings.MEDIA_URL,self.docfile.name)
	
	class Meta:
		ordering = ['docfile','filetype']

#	Table of Contents
class toc(models.Model):
	title=models.CharField(max_length=60)
	slug = models.SlugField(unique=True)
	def __unicode__(self):
		return self.title

class page(leaf):
	slug = models.SlugField(unique=True)
	title = models.CharField(max_length=100)
	body = models.TextField()
	summary = models.CharField(max_length=255,null=True,blank=True)
	
	auto_export = models.BooleanField(default=True,help_text="Uncheck this to disable automatic generation of document files.  Markdown and Plain Text will still be available.")
	docfiles = models.ManyToManyField(export_file,blank=True)
	latex_fail = models.BooleanField(default=False)
	
	book_title = models.ForeignKey(toc,null=True,blank=True,related_name='pages', on_delete=models.SET_NULL)
	book_order = models.IntegerField(default=0,blank=True)
	
	def get_title(self, raw=False):
		if self.book_title and not raw:
			return "%s:  %s" % (self.book_title.title, self.title)
		else:
			return self.title
	
	def __unicode__(self):
		return self.get_title()
	
	def get_absolute_url(self):
		return reverse('page_htm', kwargs={'cached_url':self.cat.cached_url, 'slug':self.slug})
	
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

class export_log(models.Model):
	CMD_OPTIONS = (('compile_latex','compile_latex'),('compile_epub','compile_epub'),)
	
	command = models.CharField(max_length=20, choices=CMD_OPTIONS)
	page = models.ForeignKey(page,blank=True,null=True, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	message = models.TextField()