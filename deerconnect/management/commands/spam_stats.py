#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Management Command:  spam_stats
#	Recalculate cached values for spam filter data
#	Happens asynchronously for faster form response
#	=================

from django.core.management.base import BaseCommand
from django.utils import timezone

from deerconnect.models import spam_word, spam_sender, spam_domain

class Command(BaseCommand):
	help = "Recalculates cached values for spam filter data"
	
	def handle(self, *args, **options):
		# Step 1:  Recalculate the counter for number of times a word has been used
		self.stdout.write('Recalculating keyword usage...  ')
		words = spam_word.objects.all().prefetch_related('used_by')
		for word in words:
			word.update_used_count()
		self.stdout.write('Done!\n')
		
		# Step 2:  Disable blocked email addresses if their domain is blocked
		domains = spam_domain.objects.filter(active=True, whitelist=False)
		self.stdout.write('Checking %d blocked domains...  ' % domains.count())
		disabled_count = 0
		for domain in domains:
			fixquery = spam_sender.objects.filter(active=True, email__iendswith=domain.domain)
			if fixquery.exists():
				disabled_count = disabled_count + fixquery.update(active=False, timestamp_mod=timezone.now())
		self.stdout.write('%d sender blocks disabled due to domain blocks\n' % disabled_count)
