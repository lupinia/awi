#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Forms
#	=================

import bleach
import datetime

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils import timezone
from django.utils import dateparse

from awi_access.utils import add_new_block
from deerconnect.models import spam_sender, spam_word
from deerconnect.utils import is_spam, is_spammer, form_too_soon

class contact_form(forms.Form):
	error_css_class = 'has_error';
	
	email = forms.EmailField(label='Email Address', max_length=150)
	name = forms.CharField(label='Your Name', max_length=150)
	subject = forms.CharField(label='Subject', max_length=150)
	reply_to = forms.CharField(label='reply_path', max_length=250, required=False, widget=forms.HiddenInput)
	body = forms.CharField(label='Message Body', max_length=10000, widget=forms.Textarea)
	
	def send_email(self, request):
		if form_too_soon(request):
			return (False, 'mailform_toosoon')
		
		sender_name = bleach.clean(self.cleaned_data['name'], tags=[], strip=True)
		sender_addr = bleach.clean(self.cleaned_data['email'], tags=[], strip=True)
		spam_check_sender = is_spammer(sender_addr)
		if spam_check_sender:
			if request.META.get('REMOTE_ADDR', False):
				add_new_block(request.META['REMOTE_ADDR'], unicode(request.META.get('HTTP_USER_AGENT', '')))
			return (False, 'mailform_spamaddr')
		
		if '@' in sender_name:
			sender_name = sender_name.replace('@', '_')
		
		msg = EmailMessage()
		msg.subject = '%s%s' % (settings.EMAIL_SUBJECT_PREFIX, bleach.clean(self.cleaned_data['subject'], tags=[], strip=True))
		msg.reply_to = [sender_addr,]
		msg.from_email = '%s <%s>' % (sender_name, settings.DEFAULT_FROM_EMAIL)
		
		message_template = get_template('deerconnect/email.txt')
		message_body = bleach.clean(self.cleaned_data['body'], tags=[], strip=True)
		
		spam_check_message, w = is_spam(message_body)
		if spam_check_message:
			spammer = spam_sender.objects.create(email=sender_addr, name=sender_name)
			spammer.word_used.add(spam_word.objects.filter(word__iexact=w).first())
			if request.META.get('REMOTE_ADDR', False):
				add_new_block(request.META['REMOTE_ADDR'], unicode(request.META.get('HTTP_USER_AGENT', '')))
			return (False, 'mailform_spamword')
		
		message_context = {
			'message': message_body, 
			'IP': request.META.get('REMOTE_ADDR', 'Unknown'), 
			'domain': request.META.get('HTTP_HOST', 'Unknown'), 
			'name': sender_name, 
			'email': sender_addr, 
			'subject': msg.subject,
		}
		
		if self.cleaned_data.get('reply_to', None):
			message_context['reply_path'] = self.cleaned_data['reply_to']
		
		msg.body = message_template.render(message_context)
		msg.to = [settings.DEERCONNECT_TO_EMAIL,]
		
		success = msg.send()
		if success:
			request.session['deerconnect_mailsent'] = str(timezone.now())
			cache.set('deerconnect_formsent_%s' % request.META['REMOTE_ADDR'], request.META.get('HTTP_USER_AGENT', None), 60*60*8)
			return (True, 'mailform_success')
		else:
			return (False, 'mailform_sendfail')
