#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Management Command:  Cleanup Working Directories
#	In case apps don't clean up after themselves, this should help do that for them.
#	=================

import os

from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		counter = {}
		root_dir = settings.WORKING_DIR
		for root, dirs, files in os.walk(root_dir):
			if not counter.get(root, False):
				counter[root] = {'total':0, 'deleted':0}
			
			for file in files:
				counter[root]['total'] = counter[root]['total'] + 1
				if datetime.fromtimestamp(os.path.getmtime(os.path.join(root, file))) < datetime.now() - timedelta(days=1):
					#print os.path.join(root, file)
					os.remove(os.path.join(root, file))
					counter[root]['deleted'] = counter[root]['deleted'] + 1
			
			if counter[root]['total'] > 0:
				self.stdout.write('%d files deleted from %s (%d total)\n' % (counter[root]['deleted'], root, counter[root]['total']))
		
		self.stdout.write('Cleanup of working dirs complete.\n')