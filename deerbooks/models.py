#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from os.path import join

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify

from awi_utils.utils import format_html, hash_md5, summarize
from deertrees.models import leaf

def attachment_path(instance, filename):
	name_pieces = filename.split('.')
	filename = "%s.%s" % (slugify(name_pieces[0]), name_pieces[1])
	return join('misc', filename)


@python_2_unicode_compatible
class export_file(models.Model):
	FILETYPE_OPTIONS = (
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
	
	filetype = models.CharField(max_length=10, choices=FILETYPE_OPTIONS, db_index=True, verbose_name='file type')
	docfile = models.FileField(upload_to='writing', verbose_name='file')
	timestamp_mod = models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	
	def __str__(self):
		return self.filename()
	
	def filename(self):
		return self.docfile.name
	
	def get_url(self):
		return "%s%s" % (settings.MEDIA_URL,self.docfile.name)
	
	@property
	def page_count(self):
		return self.pages.all().count()
	
	class Meta:
		ordering = ['docfile','filetype']
		verbose_name = 'document file'


#	Table of Contents (aka Book)
@python_2_unicode_compatible
class toc(models.Model):
	title = models.CharField(max_length=60, help_text="Will be appended to the title of all Pages ({Book Title}: {Page Title}).")
	slug = models.SlugField(unique=True)
	
	def __str__(self):
		return self.title
	
	@property
	def page_count(self):
		return self.pages.all().count()
	
	class Meta:
		verbose_name = 'book'


@python_2_unicode_compatible
class page(leaf):
	slug = models.SlugField(unique=True)
	title = models.CharField(max_length=100)
	body = models.TextField()
	body_hash_cur = models.TextField(default='')
	summary = models.CharField(max_length=255, null=True, blank=True, help_text="A short description of this page's content (defaults to the first 255 characters of the body text).")
	
	auto_export = models.BooleanField(default=True, db_index=True, verbose_name='auto-build document files', help_text="Uncheck this to disable automatic generation of document files, and the built-in LaTeX view.  Markdown and Plain Text will still be available if the Alternate Views option is checked.")
	alt_views = models.BooleanField(default=True, db_index=True, verbose_name='allow alternate view formats', help_text="Uncheck this to disable the built-in Plain Text and Markdown alternate views.  Uploaded document files will still be available, and the built-in LaTeX view will still be available if Automatically Build Document Files is checked.")
	showcase_default = models.BooleanField(default=False, verbose_name='show in showcase mode by default?')
	docfiles = models.ManyToManyField(export_file, blank=True, verbose_name='document files', related_name='pages')
	latex_fail = models.BooleanField(default=False, verbose_name='LaTeX compilation failure')
	
	book_title = models.ForeignKey(toc, null=True, blank=True, related_name='pages', on_delete=models.SET_NULL, help_text="Make this Page part of a Book by selecting it here.  This will create a Table of Contents linking to the other pages, and this page's title will become {Book Title}: {Page Title}.")
	book_order = models.IntegerField(default=0, blank=True, help_text='Use this field to control the position of this page within its book.  The book order does not need to be incremental; pages will be sorted in ascending order (least to greatest) using this field regardless of its value.')
	
	timestamp_revised = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='date/time revised', help_text='Date/time of last content edit.')
	
	def display_times(self):
		return_times = super(page, self).display_times()
		if self.timestamp_revised:
			revision = {'label':'Revised', 'timestamp':self.timestamp_revised,}
			if self.timedisp == 'mod' and self.revised:
				return_times.append(return_times[0])
				return_times[0] = revision
			else:
				return_times.append(revision)
		
		return return_times
	
	def get_title(self, raw=False):
		if not raw and self.book_title:
			return "%s:  %s" % (self.book_title.title, self.title)
		else:
			return self.title
	
	def __str__(self):
		return self.get_title()
	
	def get_absolute_url(self):
		return reverse('page_htm', kwargs={'cached_url':self.cat.cached_url, 'slug':self.slug})
	
	def get_summary(self,length=255):
		if length > 255:
			return summarize(body=self.body, summary=self.summary, length=length, prefer_long=True)
		else:
			return summarize(body=self.body, summary=self.summary, length=length)
	
	@property
	def revised(self):
		if self.timestamp_revised:
			return True
		else:
			return False
	
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
	
	# DEPRECATED - Use .get_summary()
	def body_summary(self,length=255):
		return self.get_summary(length)
	
	@property
	def body_html(self):
		return format_html(self.body)
	
	def get_export_filename(self):
		if self.book_title:
			return 'book.%s' % self.book_title.slug
		else:
			return self.slug
	
	def get_latex_url(self):
		if self.auto_export:
			uploaded_tex = self.docfiles.filter(filetype='tex').first()
			if uploaded_tex:
				return uploaded_tex.get_url()
			else:
				site_obj = self.sites.all().order_by('pk').first()
				if self.book_title:
					urlconf = 'book_tex'
					urlslug = self.book_title.slug
				else:
					urlconf = 'page_tex'
					urlslug = self.slug
				
				return 'http://%s%s' % (site_obj.domain, reverse(urlconf, kwargs={'cached_url':self.cat.cached_url, 'slug':urlslug}))
		else:
			return False
	
	@property
	def body_hash(self):
		return hash_md5(self.body.encode('utf-8'))
	
	def save(self, *args, **kwargs):
		if self.body_hash_cur:
			if self.body_hash_cur != self.body_hash:
				self.body_hash_cur = self.body_hash
				if self.published and not self.scheduled():
					self.timestamp_revised = timezone.now()
		else:
			self.body_hash_cur = self.body_hash
		super(page, self).save(*args, **kwargs)


@python_2_unicode_compatible
class export_log(models.Model):
	CMD_OPTIONS = (
		('compile_latex','compile_latex'),
		('compile_epub','compile_epub'),
		('no_export_deleted','no_export_deleted'),
	)
	
	command = models.CharField(max_length=20, choices=CMD_OPTIONS, help_text='The command/object that generated this log entry')
	page = models.ForeignKey(page,blank=True,null=True, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True, verbose_name='event date/time')
	message = models.TextField()
	
	def __str__(self):
		return '%s (%d): %s' % (self.page.slug, self.page.pk, self.command)
	
	class Meta:
		verbose_name = 'automatic document file build log entry'
		verbose_name_plural = 'automatic document file build log entries'


@python_2_unicode_compatible
class attachment(models.Model):
	name = models.CharField(max_length=100)
	file = models.FileField(upload_to=attachment_path)
	timestamp_mod=models.DateTimeField(auto_now=True, db_index=True, verbose_name='date/time modified')
	timestamp_post=models.DateTimeField(default=timezone.now, db_index=True, verbose_name='date/time created')
	
	def __str__(self):
		return self.name
	
	def get_url(self):
		return "%s%s" % (settings.MEDIA_URL,self.file.name)

