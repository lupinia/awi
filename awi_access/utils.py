#	Awi Access (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions/Objects
#	=================

from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from awi_access.models import blocked_ip

#	Checks a given address, and returns True if it's blocked
def is_blocked(address, raise_403=False):
	status = True
	if address:
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
	cache.set('blocked_ip_%s' % address, True, 60*60*24*7)
	return blocked_ip.objects.create(address=address, user_agent=agent, active=True)
