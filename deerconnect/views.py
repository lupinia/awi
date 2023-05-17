#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

import datetime

from django.core.urlresolvers import reverse
from django.utils import dateparse
from django.utils import timezone
from django.views.generic.edit import FormView

from awi_access.models import access_query
from deerconnect.forms import contact_form
from deerconnect.models import contact_link

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
		context['title_page'] = "Contact Information"
		
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		context['breadcrumbs'].append({'url':reverse('contact'), 'title':'Contact'})
		
		if self.request.session.get('deerconnect_success_msg', False):
			context['form'] = ''
			context['error'] = 'mailform_success'
			self.request.session['deerconnect_success_msg'] = False
		elif self.request.session.get('deerconnect_mailsent', False):
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


def contact_widget(parent=False, parent_type=False, request=False):
	if parent_type == 'category' and parent:
		ancestors = parent.get_ancestors(include_self=True)
		contact_links = contact_link.objects.filter(cat__in=ancestors).filter(access_query(request)).order_by('-timestamp_mod')
		if contact_links:
			return contact_links
		else:
			return False
	else:
		return False
