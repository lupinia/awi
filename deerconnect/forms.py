#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Forms
#	=================

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils import dateparse
import bleach
import datetime

class contact_form(forms.Form):
	error_css_class = 'has_error';
	
	email = forms.EmailField(label='Email Address', max_length=150)
	name = forms.CharField(label='Your Name', max_length=150)
	subject = forms.CharField(label='Subject', max_length=150)
	body = forms.CharField(label='Message Body', max_length=5000, widget=forms.Textarea)
	
	def send_email(self, request):
		if request.session.get('deerconnect_mailsent',False):
			last_message = dateparse.parse_datetime(request.session.get('deerconnect_mailsent',False))
			expiration = datetime.timedelta(days=1)
			if last_message > timezone.now() - expiration:
				return False
		
		from django.template.loader import get_template
		from django.template import Context
		
		msg = {}
		msg['subject'] = '%s%s' % (settings.EMAIL_SUBJECT_PREFIX, bleach.clean(self.cleaned_data['subject'], tags=[], strip=True))
		msg['from_email'] = bleach.clean(self.cleaned_data['email'], tags=[], strip=True)
		
		message_template = get_template('deerconnect/email.txt')
		message_body = bleach.clean(self.cleaned_data['body'], tags=[], strip=True)
		
		message_context = {
			'message': message_body, 
			'IP': request.META.get('REMOTE_ADDR'), 
			'domain': request.META.get('HTTP_HOST'), 
			'name': bleach.clean(self.cleaned_data['name'], tags=[], strip=True), 
			'email': msg['from_email'], 
			'subject': msg['subject'],
		}
		d = Context(message_context)
		
		msg['message'] = message_template.render(d)
		msg['recipient_list'] = [settings.DEERCONNECT_TO_EMAIL,]
		
		success = send_mail(**msg)
		if success:
			request.session['deerconnect_mailsent'] = str(timezone.now())
			return True
		else:
			return False
