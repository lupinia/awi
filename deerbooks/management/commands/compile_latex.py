#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Management Command:  compile_latex
#	Assembles PDF, DVI, and PS files from LaTeX source.
#	=================

import os.path
import subprocess
import urllib

from django.conf import settings
from django.core.files import File
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.db.models import Q

from awi_access.models import access_query
from deerbooks.models import export_file, page, export_log

class Command(BaseCommand):
	help = "Assembles PDF, DVI, and PS files from LaTeX source."
	cur_page = False
	
	def log(self, msg, page_override=False):
		if page_override:
			return export_log.objects.create(command='compile_latex', page=page_override, message=msg)
		elif self.cur_page:
			return export_log.objects.create(command='compile_latex', page=self.cur_page, message=msg)
		else:
			return export_log.objects.create(command='compile_latex', message=msg)
	
	def notify(self, status='unknown'):
		msg = {}
		
		if status is 'success':
			# Yay!  :D
			msg['subject'] = 'LaTeX Compilation Succeeded on Page %d (%s)' % (self.cur_page.pk, self.cur_page.slug)
			msg['message'] = 'LaTeX compilation on page %d ("%s", slug: %s) succeeded.' % (self.cur_page.pk, self.cur_page.get_title(), self.cur_page.slug)
		elif status is 'failure':
			# Not yay!  :(
			if self.cur_page:
				msg['subject'] = 'LaTeX Compilation Failed on Page %d (%s)' % (self.cur_page.pk, self.cur_page.slug)
				msg['message'] = 'LaTeX compilation failed on page %d ("%s", slug: %s) succeeded.' % (self.cur_page.pk, self.cur_page.get_title(), self.cur_page.slug)
			else:
				msg['subject'] = 'LaTeX Compilation Failed:  Unknown Page'
				msg['message'] = 'LaTeX compilation failed on an unknown page.'
		else:
			# WTF?
			msg['subject'] = 'LaTeX Compilation Error'
			msg['message'] = 'LaTeX compilation encountered an unknown error.'
		
		success = mail_admins(**msg)
		if success:
			return True
		else:
			return False
	
	def get_tex(self, source_url, dest_name):
		try:
			texfile_dl = urllib.urlretrieve(source_url, '%s/%s' % (settings.DEERBOOKS_CACHE_DIR, dest_name))
			texfile_check = open(texfile_dl[0])
			texfile_check.close()
			self.log('Successfully retrieved TeX file (%s)' % dest_name)
			return texfile_dl[0]
		except:
			import sys,traceback
			self.log('Manage.py LaTeX compile error:  Unable to retrieve TeX file.  Details:  %s (%s) - %s' % (str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2])))
			raise CommandError(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
			return False
	
	def handle(self, *args, **options):
		try:
			# Figure out the next one that needs to be compiled
			texfile = False
			old_docfiles = []
			
			pages = page.objects.filter(Q(auto_export=True) & Q(latex_fail=False)).exclude(cat_id=75).order_by('timestamp_mod')
			for page_obj in pages:
				old_docfiles = []
				page_docs = page_obj.docfiles.all().order_by('filetype')
				if page_docs.exists():
					# Things might get weird here.  We have docfiles already.
					for doc in page_docs:
						if doc.filetype in ['ps','pdf','dvi']:
							if doc.timestamp_mod > page_obj.timestamp_mod:
								# If we're here, it means that the current page has docfiles newer than its last mod date
								# Which means we're not going to compile it.
								break
							else:
								old_docfiles.append(doc)
						elif doc.filetype == 'tex':
							# We have our LaTeX file!
							dest_name = doc.docfile.name.split('/')
							dest_name.reverse()
							filename = dest_name[0].replace('.tex','')
							texfile = self.get_tex(doc.docfile.url, '%s.tex' % filename)
							if texfile:
								self.cur_page = page_obj
								self.log('LaTeX will be compiled for page %d (%s)' % (self.cur_page.pk, self.cur_page.slug))
								self.log('Using LaTeX source from attached docfiles')
								break
				
				else:
					# This is the one we're going to work with, it's all shiny and new and stuff.
					self.cur_page = page_obj
					self.log('LaTeX will be compiled for page %d (%s)' % (self.cur_page.pk, self.cur_page.slug))
					break
				
				if self.cur_page:
					break
			
			if self.cur_page and not texfile:
				# Well, we don't have an uploaded LaTeX source file, so we'll have to download one.
				# First step:  Figure out which domain to use.
				# Prefer site 1; else, use site 2
				self.log("Downloading views-based LaTeX source file")
				page_sites = self.cur_page.sites.all()
				dl_domain = False
				for site in page_sites:
					if site.pk == 1:
						dl_domain = 'seneca.lupinia.net'
					elif not dl_domain:
						dl_domain = 'beta.softpaw.eu'
				
				#if not 'www' in dl_domain:
					#dl_domain = 'www.%s' % dl_domain
				
				if self.cur_page.book_title:
					dl_path = reverse('book_tex',kwargs={'cached_url':self.cur_page.cat.cached_url,'slug':self.cur_page.book_title.slug,})
					filename = 'book.%s' % self.cur_page.book_title.slug
				else:
					dl_path = reverse('page_tex',kwargs={'cached_url':self.cur_page.cat.cached_url,'slug':self.cur_page.slug,})
					filename = self.cur_page.slug
				
				dl_url = 'http://%s%s' % (dl_domain, dl_path)
				texfile = self.get_tex(dl_url, '%s.tex' % filename)
			
			if not texfile:
				raise CommandError()
			else:
				self.log("Successfully downloaded %s.tex" % filename)
			
			# We should now have a LaTeX file.
			# Let's compile it.
			latex_command = ['rubber','--ps','--pdf','--inplace',texfile]
			self.log("Beginning compilation with command:  \n%s" % ' '.join(latex_command))
			compile_status = subprocess.check_output(latex_command,stderr=subprocess.STDOUT)
			self.log("Compilation complete!  Command output:  \n%s" % compile_status)
			
			new_docfiles = []
			new_types = ['ps','pdf','dvi']
			completed_types = []
			if old_docfiles:
				for update_file in old_docfiles:
					cur_file_obj = File(open('%s/%s.%s' % (settings.DEERBOOKS_CACHE_DIR,filename,update_file.filetype),'rb'))
					update_file.docfile.save('%s.%s' % (filename,update_file.filetype),cur_file_obj)
					update_file.save()
					cur_file_obj.close()
					completed_types.append(update_file.filetype)
					self.log("Successfully updated existing %s file." % update_file.filetype)
			
			for new_type in new_types:
				cur_file_obj = File(open('%s/%s.%s' % (settings.DEERBOOKS_CACHE_DIR,filename,new_type),'rb'))
				new_doc = export_file(filetype=new_type)
				new_doc.docfile.save('%s.%s' % (filename,new_type),cur_file_obj)
				new_doc.save()
				cur_file_obj.close()
				completed_types.append(new_type)
				new_docfiles.append(new_doc)
				self.log("Successfully created new %s file." % new_doc.filetype)
			
			if new_docfiles:
				self.cur_page.docfiles.add(*new_docfiles)
				self.log("Successfully attached new docfiles to page %d (%s)." % (self.cur_page.pk, self.cur_page.slug))
				if self.cur_page.book_title:
					related_pages = self.cur_page.book_title.page_set.all()
					for other_page in related_pages:
						if other_page is not self.cur_page:
							other_page.docfiles.add(*new_docfiles)
							self.log("Successfully attached new docfiles to page %d (%s)." % (other_page.pk, other_page.slug), other_page)
			
			self.log("Compile operation complete!")
			self.stdout.write('Operation Complete on %d (%s)' % (self.cur_page.pk, self.cur_page.slug))
			self.notify('success')
			
		except:
			import sys,traceback
			self.notify('failure')
			self.log('Manage.py LaTeX compile error:  %s (%s) - %s' % (str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2])))
			if self.cur_page:
				self.cur_page.latex_fail = True
				self.cur_page.save()
			raise CommandError(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
