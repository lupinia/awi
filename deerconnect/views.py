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
from deerfind.utils import shortcode_lookup

class contact_page(FormView):
	template_name = 'deerconnect/contact.html'
	form_class = contact_form
	success_url = '/contact/'
	reply_form = False
	reply_obj = None
	reply_title = None
	reply_path = None
	
	def get(self, request, *args, **kwargs):
		if request.GET.get('reply_to', False):
			reply_parsed = request.GET.get('reply_to', '').split('-')
			if len(reply_parsed) > 1:
				reply_type = reply_parsed[0]
				reply_pk = reply_parsed[1]
				
				if reply_pk and len(reply_type) == 1:
					reply_obj, error = shortcode_lookup(reply_type, reply_pk)
					
					if reply_obj:
						if hasattr(reply_obj, 'can_view'):
							reply_view_check, reply_view_error = reply_obj.can_view(request)
						else:
							reply_view_check = True
						
						if reply_view_check:
							self.reply_form = True
							self.reply_obj = reply_obj
							self.reply_title = unicode(reply_obj)
							
							if hasattr(reply_obj, 'get_absolute_url'):
								self.reply_path = reply_obj.get_absolute_url()
							else:
								self.reply_path = '%s (%s, pk %d)' % (context['reply_title'], settings.DEERFIND_SHORTCODE_TYPES[reply_type], reply_pk)
		
		return super(contact_page, self).get(request, *args, **kwargs)
	
	def get_initial(self):
		initial = super(contact_page, self).get_initial()
		if self.reply_form and self.reply_path:
			initial['reply_to'] = self.reply_path
			initial['subject'] = 'RE: %s' % self.reply_title
		
		return initial
	
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
		
		if self.reply_form and self.reply_obj:
			context['reply_form'] = getattr(self, 'reply_form', False)
			context['reply_title'] = getattr(self, 'reply_title', '')
			context['reply_path'] = getattr(self, 'reply_path', '')
			context['title_page'] += ' - Reply to: %s' % context['reply_title']
		
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
