#	Awi Access (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

import datetime

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.template import loader
from django.utils import dateparse
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from awi_access.forms import age_verify_form
from awi_access.models import check_mature, user_settings

class age_verify(FormView):
	template_name = 'awi_access/age_form_embed.html'
	form_class = age_verify_form
	success_url = '/accounts/age_form_embed/'
	
	def get_success_url(self):
		if self.request.GET.get('return_to', False):
			return self.request.GET.get('return_to', False)
		else:
			return self.success_url
	
	def form_valid(self, form):
		dob_valid = form.validate_age()
		
		if self.request.user.is_authenticated():
			meta, meta_status = user_settings.objects.get_or_create(user=self.request.user)
			meta.mature_available = dob_valid
			meta.show_mature = dob_valid
			meta.age_check_date = timezone.now()
			meta.save()
		else:
			if dob_valid:
				self.request.session['awi_mature_access'] = str(timezone.now() + datetime.timedelta(days=2))
			else:
				self.request.session['awi_mature_denied'] = True
		
		if dob_valid:
			cache.clear()
		
		self.request.session['awi_age_form_complete'] = True
		return super(age_verify, self).form_valid(form)
	
	def get_context_data(self, **kwargs):
		context = super(age_verify, self).get_context_data(**kwargs)
		context['honeypot_field_name'] = settings.HONEYPOT_FIELD_NAME_AWIACCESS
		
		mature = check_mature(self.request)
		if mature[0]:
			context['form'] = ''
			context['error'] = 'access_mature_granted'
		elif mature[1] != 'access_mature_prompt':
			context['form'] = ''
			context['error'] = mature[1]
		
		if self.request.session.get('awi_age_form_complete', False):
			self.request.session['awi_age_form_complete'] = False
			context['success'] = True
		
		# Metadata
		context['title_page'] = "Age Verification Form"
		
		return context


class age_verify_full(age_verify):
	template_name = 'awi_access/age_form.html'
	success_url = '/accounts/age_form/'
	
	def get_context_data(self, **kwargs):
		context = super(age_verify_full, self).get_context_data(**kwargs)
		
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		context['breadcrumbs'].append({'url':reverse('age_form'), 'title':'Age Verification'})
		
		return context


class settings_page(TemplateView):
	template_name='awi_access/settings.html'
	
	def get_context_data(self, **kwargs):
		context = super(settings_page,self).get_context_data(**kwargs)
		
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		context['breadcrumbs'].append({'url':reverse('settings'), 'title':'Settings'})
		
		mature_check = check_mature(self.request)
		if self.request.user.is_authenticated():
			context['user_meta'], meta_status = user_settings.objects.get_or_create(user=self.request.user)
		
		if context.get('user_meta',False):
			context['age_verify_date'] = context.get('user_meta',False).age_check_date
		elif mature_check[0]:
			context['age_verify_end_date'] = dateparse.parse_datetime(self.request.session.get('awi_mature_access', False))
		
		if self.request.GET.get('mature', False) and not mature_check[1] == 'access_mature_denied':
			changed = False
			if self.request.GET.get('mature', False) == 'hide' and mature_check[0]:
				if context.get('user_meta', False):
					context['user_meta'].show_mature = False
					context['user_meta'].save()
					changed = True
				else:
					self.request.session['awi_mature_access'] = False
					changed = True
			
			elif self.request.GET.get('mature', False) == 'show' and not mature_check[0]:
				# Only logged-in users who've already passed the form get to toggle this bi-directionally.
				if context.get('user_meta', False):
					if context['user_meta'].mature_available and context['user_meta'].age_check_date:
						context['user_meta'].show_mature = True
						context['user_meta'].save()
						changed = True
			
			if changed:
				cache.clear()
		
		# Metadata
		context['title_page'] = "Settings"
		
		return context

def denied_error(request, exception=None):
	"""Custom error page for 403 errors"""
	template=loader.get_template('awi_access/403.html')
	if request.META.get('QUERY_STRING',False):
		context_path=request.path+'?'+request.META.get('QUERY_STRING','')
	else:
		context_path=request.path
	
	context = {
		'bad_url':context_path,
		'title_page':"Access Denied (HTTP 403)",
		'response_code':'403',
		'response_code_name':'Forbidden',
	}
	
	return HttpResponseForbidden(content=template.render(context, request), content_type='text/html; charset=utf-8')
