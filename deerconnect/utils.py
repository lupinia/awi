#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions/Objects
#	=================

import datetime

from django.core.cache import cache
from django.utils import dateparse, timezone

from deerconnect.models import spam_sender, spam_word

#	Check a string for spam words
def is_spam(message):
	sensitive = spam_word.objects.filter(case_sensitive=True, active=True).values_list('word', flat=True)
	insensitive = spam_word.objects.filter(case_sensitive=False, active=True).values_list('word', flat=True)
	
	if sensitive.exists():
		for w in sensitive:
			if w in message:
				return (True, w)
	
	if insensitive.exists():
		message_lower = message.lower()
		for w in insensitive:
			if w.lower() in message_lower:
				return (True, w)
	
	return (False, '')

#	Strip extraneous characters from an email address
#	This is merely a formatting filter, so if it fails, it should just return its input unaltered
def fix_email(address, strip_dots=True, strip_plus=True):
	if '@' not in address or address.count('@') > 1:
		return address
	
	address = address.lower()
	uname, domain = address.split('@')
	if '.' in uname and strip_dots:
		# Gmail has kinda broken email with their handling of dots in addresses
		# But it's also incredibly easy for a spammer to evade a block by just messing with the dots
		uname = uname.replace('.', '')
	if '+' in uname and strip_plus:
		uname_parts = uname.split('+')
		uname = uname_parts[0]
	
	return '%s@%s' % (uname, domain)

#	Check whether an email address is a spam sender
#	Not doing a direct DB query for security reasons
def is_spammer(sender):
	sender = fix_email(sender)
	spammers = spam_sender.objects.all().values_list('email', flat=True)
	if sender in spammers:
		return True
	else:
		return False

#	Check whether the contact form has already been submitted
def form_too_soon(request):
	if request.META.get('REMOTE_ADDR', '') and request.META.get('HTTP_USER_AGENT', False):
		cache_check = cache.get('deerconnect_formsent_%s' % request.META['REMOTE_ADDR'])
		if cache_check is not None:
			if cache_check == request.META.get('HTTP_USER_AGENT', 'Unknown'):
				return True
	
	if request.session.get('deerconnect_mailsent',False):
		last_message = dateparse.parse_datetime(request.session['deerconnect_mailsent'])
		expiration = datetime.timedelta(hours=8)
		if last_message > timezone.now() - expiration:
			return True
		else:
			request.session['deerconnect_mailsent'] = None
	
	return False
