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

from deerconnect.models import spam_sender, spam_word, spam_domain

#	Check a string for spam words
def is_spam(message, find_all=True):
	detected = False
	words = []
	sensitive = spam_word.objects.filter(case_sensitive=True, active=True).values_list('word', flat=True)
	insensitive = spam_word.objects.filter(case_sensitive=False, active=True).values_list('word', flat=True)
	
	if sensitive.exists():
		for w in sensitive:
			if w in message:
				if find_all:
					detected = True
					words.append(w)
				else:
					return (True, [w])
	
	if insensitive.exists():
		message_lower = message.lower()
		for w in insensitive:
			if w.lower() in message_lower:
				if find_all:
					detected = True
					words.append(w)
				else:
					return (True, [w])
	
	return (detected, words)

#	Basic, just split an email address into username and domain
def split_email(address):
	if '@' not in address or address.count('@') > 1:
		return (address, '')
	
	return address.split('@')

#	Strip extraneous characters from an email address
#	This is merely a formatting filter, so if it fails, it should just return its input unaltered
def fix_email(address, strip_dots=True, strip_plus=True):
	if '@' not in address or address.count('@') > 1:
		return address
	
	address = address.lower()
	uname, domain = split_email(address)
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
	uname, domain = split_email(sender)
	domain_list = spam_domain.objects.filter(active=True, whitelist=False).values_list('domain', flat=True)
	whitelist = spam_domain.objects.filter(active=True, whitelist=True).values_list('domain', flat=True)
	if domain in domain_list:
		return True
	else:
		if domain in whitelist:
			spammers = spam_sender.objects.filter(active=True).values_list('email', flat=True)
			if sender in spammers:
				return True
			else:
				return False
		else:
			return False

def record_spammer(sender, name, words=[]):
	sender_uname, sender_domain = split_email(sender)
	whitelist = spam_domain.objects.filter(whitelist=True).values_list('domain', flat=True)
	to_update = {'name':name,}
	if sender_domain not in whitelist:
		spam_domain.objects.get_or_create(domain=sender_domain, whitelist=False)
		to_update['active'] = False
	
	spammer, created = spam_sender.objects.get_or_create(defaults=to_update, email=fix_email(sender))
	tripped_words = spam_word.objects.filter(word__in=words)
	if tripped_words.exists():
		spammer.word_used.add(*tripped_words)

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
