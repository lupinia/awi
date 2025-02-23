#	DeerConnect (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView

from awi_access.models import access_query
from awi_access.utils import is_blocked
from deerconnect.forms import contact_form
from deerconnect.models import contact_link
from deerconnect.utils import form_too_soon
from deerfind.utils import shortcode_lookup

class contact_page(FormView):
	template_name = 'deerconnect/contact.html'
	form_class = contact_form
	success_url = '/contact/'
	reply_form = False
	reply_obj = None
	reply_title = None
	reply_path = None
	send_status = None
	
	def dispatch(self, *args, **kwargs):
		# Check whether the IP address is blocked
		is_blocked(self.request.META.get('REMOTE_ADDR', ''), raise_403=True)
		return super(contact_page,self).dispatch(*args, **kwargs)
	
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
							self.reply_title = unicode(reply_obj) # type: ignore
							
							if hasattr(reply_obj, 'get_absolute_url'):
								self.reply_path = reply_obj.get_absolute_url()
							else:
								self.reply_path = '%s (%s, pk %d)' % (self.reply_title, settings.DEERFIND_SHORTCODE_TYPES[reply_type], reply_pk)
		
		return super(contact_page, self).get(request, *args, **kwargs)
	
	def get_initial(self):
		initial = super(contact_page, self).get_initial()
		if self.reply_form and self.reply_path:
			initial['reply_to'] = self.reply_path
			if not initial.get('subject', False):
				initial['subject'] = 'RE: %s' % self.reply_title
		
		return initial
	
	def form_valid(self, form):
		success, self.send_status = form.send_email(self.request)
		if success:
			if not self.request.user.is_authenticated():
				self.request.session['deerconnect_contact_form_success'] = True
			return super(contact_page, self).form_valid(form)
		else:
			return super(contact_page, self).form_invalid(form)
	
	def get_context_data(self, **kwargs):
		context = super(contact_page, self).get_context_data(**kwargs)
		context['title_page'] = "Contact Information"
		
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		context['breadcrumbs'].append({'url':reverse('contact'), 'title':'Contact'})
		
		# Apparently there's no way around using a session variable for this, so we still have to handle that.
		if self.request.session.get('deerconnect_contact_form_success', False) and not self.request.user.is_authenticated():
			context['form'] = ''
			context['error'] = 'mailform_success'
			self.request.session['deerconnect_contact_form_success'] = False
		elif self.send_status:
			context['error'] = self.send_status
			if self.send_status in ['mailform_success', 'mailform_spamaddr', 'mailform_spamword', 'mailform_toosoon']:
				context['form'] = ''
		elif form_too_soon(self.request) and not self.request.user.is_authenticated():
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
