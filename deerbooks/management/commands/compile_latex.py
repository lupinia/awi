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

from deerbooks.models import export_file, page, export_log

class Command(BaseCommand):
	help = "Assembles PDF, DVI, and PS files from LaTeX source."
	cur_page = False
	types = ['ps','pdf','dvi']
	
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
				msg['message'] = 'LaTeX compilation failed on page %d ("%s", slug: %s).' % (self.cur_page.pk, self.cur_page.get_title(), self.cur_page.slug)
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
			tex_custom = False
			old_docfiles = []
			
			if len(settings.DEERBOOKS_LATEX_CMD) < 1:
				# Executable command missing!
				raise OSError(1, "LaTeX executable command missing")
			
			pages = page.objects.filter(Q(auto_export=True) & Q(latex_fail=False) & Q(published=True)).exclude(cat_id=75).order_by('timestamp_mod')
			for page_obj in pages:
				old_docfiles = []
				page_docs = page_obj.docfiles.filter(filetype__in=self.types).order_by('filetype')
				if page_docs:
					# Things might get weird here.  We have docfiles already.
					for doc in page_docs:
						if doc.timestamp_mod > page_obj.timestamp_mod:
							# If we're here, it means that the current page has docfiles newer than its last mod date
							# Which means we're not going to compile it.
							break
						else:
							old_docfiles.append(doc)
					
					if old_docfiles:
						# If we're here, it means that the current page has stale doc files, and no custom tex file.
						self.cur_page = page_obj
						self.log('LaTeX will be compiled for page %d (%s)' % (self.cur_page.pk, self.cur_page.slug))
						break
				
				else:
					# This is the one we're going to work with, it's all shiny and new and stuff.
					self.cur_page = page_obj
					self.log('LaTeX will be compiled for new page %d (%s)' % (self.cur_page.pk, self.cur_page.slug))
					break
				
				if self.cur_page:
					break
			
			if self.cur_page:
				filename = self.cur_page.get_export_filename()
				tex_url = self.cur_page.get_latex_url()
				
				if tex_url:
					self.log("Attempting to download %s" % tex_url)
					texfile = self.get_tex(tex_url, '%s.tex' % filename)
				else:
					texfile = False
			
			if self.cur_page and not texfile:
				raise CommandError()
			elif self.cur_page and texfile:
				self.log("Successfully downloaded %s.tex" % filename)
			
				# We should now have a LaTeX file.
				# Let's compile it.
				latex_command = settings.DEERBOOKS_LATEX_CMD
				latex_command.append(texfile)
				self.log("Beginning compilation with command:  \n%s" % ' '.join(latex_command))
				compile_status = subprocess.check_output(latex_command,stderr=subprocess.STDOUT)
				self.log("Compilation complete!  Command output:  \n%s" % compile_status)
				
				new_docfiles = []
				new_types = self.types
				completed_types = []
				if old_docfiles:
					for update_file in old_docfiles:
						cur_file_obj = File(open('%s/%s.%s' % (settings.DEERBOOKS_CACHE_DIR,filename,update_file.filetype),'rb'))
						update_file.docfile.delete()
						update_file.docfile.save('%s.%s' % (filename,update_file.filetype),cur_file_obj)
						update_file.save()
						cur_file_obj.close()
						completed_types.append(update_file.filetype)
						self.log("Successfully updated existing %s file." % update_file.filetype)
				else:
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
						if tex_custom:
							related_pages = tex_custom.pages.all()
						elif self.cur_page.book_title:
							related_pages = self.cur_page.book_title.pages.all()
						else:
							related_pages = False
						
						if related_pages:
							for other_page in related_pages:
								if other_page is not self.cur_page:
									other_page.docfiles.add(*new_docfiles)
									self.log("Successfully attached new docfiles to page %d (%s)." % (other_page.pk, other_page.slug), other_page)
				
				self.log("Compile operation complete!")
				self.stdout.write('Operation Complete on %d (%s)' % (self.cur_page.pk, self.cur_page.slug))
				self.notify('success')
			
			else:
				# Nothing to do!
				self.log("No documents to compile.")
				self.stdout.write("No documents to compile.")
			
		except:
			import sys,traceback
			self.notify('failure')
			self.log('Manage.py LaTeX compile error:  %s (%s) - %s' % (str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2])))
			if self.cur_page:
				self.cur_page.latex_fail = True
				self.cur_page.save()
			raise CommandError(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
