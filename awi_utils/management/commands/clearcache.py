#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Management Command:  Clear Cache
#	Something Django really should include out of the box:  A tool to clear the cache via the command line.
#	=================

from django.core.management.base import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		cache.clear()
		self.stdout.write('Cleared cache\n')