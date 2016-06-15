#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Management Command:  health_check
#	Checks links to ensure that they're still valid.
#	=================

import requests

from django.conf import settings
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from deerconnect.models import link, contact_link

class Command(BaseCommand):
	help = "Assembles PDF, DVI, and PS files from LaTeX source."
	cur_link = False
	
	def notify(self, status='unknown', code=0):
		msg = {}
		
		if status is 'success':
			# Yay!  :D
			# Don't spam me, though.
			pass
		elif status is 'failure':
			# Not yay!  :(
			if self.cur_link:
				msg['subject'] = 'Health Check Failed on Link %d (%s)' % (self.cur_link.pk, self.cur_link.url)
				msg['message'] = 'Health check failed on link %d ("%s", url: %s).  Status code:  %d' % (self.cur_link.pk, self.cur_link.label, self.cur_link.url, code)
			else:
				msg['subject'] = 'Health Check Failed:  Unknown Link'
				msg['message'] = 'Health check failed on an unknown link.  Status code:  %d' % code
		else:
			# WTF?
			msg['subject'] = 'Link Health Check Error'
			msg['message'] = 'Link health check encountered an unknown error.'
		
		success = mail_admins(**msg)
		if success:
			return True
		else:
			return False
	
	def check_link(self, url):
		agent = {'user-agent': settings.DEERCONNECT_HEALTHCHECK_USERAGENT}
		r = requests.head(url, headers=agent)
		if r.status_code == 200:
			status = True
		else:
			status = False
		
		return (status, r.status_code)
	
	def check_links_bulk(self, links):
		failure_count = 0
		for cur in links:
			self.cur_link = cur
			check = self.check_link(self.cur_link.url)
			if not check[0]:
				self.notify('failure',check[1])
				self.cur_link.healthy=False
				self.cur_link.published=False
				self.cur_link.save()
				failure_count = failure_count + 1
		
		return failure_count
	
	def handle(self, *args, **options):
		try:
			links = link.objects.filter(Q(published=True) & Q(healthy=True)).exclude(cat_id=75)
			fail_count = self.check_links_bulk(links)
			self.stdout.write("Health check complete on link objects:  %d failures." % fail_count)
		except:
			import sys,traceback
			self.notify('failure')
			raise CommandError(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
