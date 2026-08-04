#	Dagasi - Content Security (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions/Objects
#	=================

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from awi_access.models import blocked_ip
from watchdeer.utils import notify

#	Checks a given address, and returns True if it's blocked
def is_blocked(address, raise_403=False):
	status = True
	if address:
		if address in settings.INTERNAL_IPS:
			# Never block an internal IP address
			return False
		
		check = cache.get('blocked_ip_%s' % address)
		if check is None:
			check = blocked_ip.objects.filter(active=True, address=address).exists()
			cache.set('blocked_ip_%s' % address, check, 60*60*24*7)
	
	if check:
		# IP is banned
		status = True
	else:
		status = False
	
	if raise_403 and status:
		raise PermissionDenied
	else:
		return status

def add_new_block(address, agent=None):
	if address not in settings.INTERNAL_IPS:
		cache.set('blocked_ip_%s' % address, True, 60*60*24*7)
		return blocked_ip.objects.update_or_create(address=address, defaults={'user_agent':agent, 'active':True})[0]
	else:
		notify('Trusted IP Block Attempt', 'The trusted IP address %s performed an action that would have resulted in a block if it were not a trusted IP address.  Investigate further if this was unexpected.' % address)
		return (None, False)
