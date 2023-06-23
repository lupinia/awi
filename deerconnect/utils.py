#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility Functions/Objects
#	=================

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