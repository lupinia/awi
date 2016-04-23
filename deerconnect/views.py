#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.views.generic.edit import FormView
from django.utils import timezone
from django.utils import dateparse
import datetime

from deerconnect.forms import contact_form
from deerconnect.models import contact_link
from awi_access.models import access_query

class contact_page(FormView):
	template_name = 'deerconnect/contact.html'
	form_class = contact_form
	success_url = '/contact/'
	
	def form_valid(self, form):
		success = form.send_email(self.request)
		if success:
			return super(contact_page, self).form_valid(form)
		else:
			return super(contact_page, self).form_invalid(form)
	
	def get_context_data(self, **kwargs):
		context = super(contact_page, self).get_context_data(**kwargs)
		
		if self.request.session.get('deerconnect_mailsent',False):
			last_message = dateparse.parse_datetime(self.request.session.get('deerconnect_mailsent',False))
			expiration = datetime.timedelta(days=1)
			if last_message > timezone.now() - expiration:
				context['form'] = ''
				context['error'] = 'mailform_toosoon'
		
		contactinfo = contact_link.objects.filter(access_query(self.request)).order_by('-im','-timestamp_mod')
		if contactinfo:
			for link in contactinfo:
				if link.im:
					if not context.get('links_im',False):
						context['links_im'] = []
					context['links_im'].append(link)
				
				else:
					if not context.get('links',False):
						context['links'] = []
					context['links'].append(link)
		
		return context