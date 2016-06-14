#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Management Command:  compile_latex
#	Assembles PDF, DVI, and PS files from LaTeX source.
#	=================

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from deerbooks.models import export_file, page, export_log

class Command(BaseCommand):
	help = "Sets auto_export to False if published is False and category is Trash."
	
	def log(self, msg, page_override=False):
		if page_override:
			return export_log.objects.create(command='no_export_deleted', page=page_override, message=msg)
		else:
			return export_log.objects.create(command='no_export_deleted', message=msg)
	
	def handle(self, *args, **options):
		try:
			pages = page.objects.filter(Q(auto_export=True) & Q(published=False) & Q(cat_id=75))
			if pages.exists():
				success_count = pages.update(auto_export=False)
				for updated in pages:
					if updated.auto_export:
						self.log('Unable to disable auto_export on deleted page %d.' % updated.pk, updated)
					else:
						self.log('Auto_export disabled on deleted page %d.' % updated.pk, updated)
				
				self.stdout.write('Fixed %d pages' % success_count)
			else:
				self.stdout.write('No deleted pages are marked for export.')
		
		except:
			import sys,traceback
			self.log('Manage.py auto_export cleanup failure:  %s (%s) - %s' % (str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2])))
			raise CommandError(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
