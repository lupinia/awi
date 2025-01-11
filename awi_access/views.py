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
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.template import loader
from django.utils import dateparse
from django.utils import timezone
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView

from awi.utils.types import is_int
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


#	Base view for objects that use access checks
class access_view(DetailView):
	can_view = True
	view_restriction = 'no_object'
	can_edit = False
	edit_restriction = ''
	is_public = True
	public_restriction = ''
	
	edit_success = None
	edit_error = ''
	edit_redirect_to = None
	edit_cmd_handled = None
	
	def edit_object(self, obj):
		"""
		Extendable method for handling inline edit commands
		Executed within get_object() if permissions check succeeds and command is present
		Put additional commands after this function (put the super() call first)
		"""
		self.edit_success = False
		self.edit_cmd_handled = True
		self.edit_error = 'quickedit_unknown'
		
		# Pull known arguments
		cmd = self.request.GET.get('alitelvdi', '')
		target = self.request.GET.get('diyosdi', None)
		audience = self.request.GET.get('yvwi', None)
		days = self.request.GET.get('sesdi', None)
		
		# Commands that don't require any extra parameters
		quick_cmd_map = {
			'feature': {'field':'featured', 'value':True,},
			'unfeature': {'field':'featured', 'value':False,},
			'publish': {'field':'published', 'value':True,},
			'unpublish': {'field':'published', 'value':False,},
			'nsfw': {'field':'mature', 'value':True,},
			'sfw': {'field':'mature', 'value':False,},
		}
		
		if cmd == 'touch':
			# Simply re-save the object to update its last-modified timestamp
			# Commands issued in this function usually don't do that
			obj.save()
			self.edit_success = True
		
		elif cmd in quick_cmd_map.keys():
			# Basic field changes/toggles that require no other parameters
			# Defined in the dictionary above
			self.edit_success = obj.quick_edit(**quick_cmd_map[cmd])
		
		elif cmd == 'chmod':
			level = None
			if audience == 'u':
				# Private
				level = 2
			elif audience == 'g':
				# Logged-in users
				level = 1
			elif audience == 'o':
				# Public
				level = 0
			
			if level is None:
				self.edit_success = False
				self.edit_error = 'quickedit_chmod_invalid'
			else:
				self.edit_success = obj.quick_edit('security', level)
		
		elif cmd == 'accessgrant' or cmd == 'accessreset':
			if days == 'permanent':
				days = 0
			elif is_int(days):
				days = int(days)
			else:
				days = None
			
			if days is None:
				self.edit_success = False
				self.edit_error = 'quickedit_accesscode_age_invalid'
			else:
				# If we're here, we have everything we need, so let's walk through the logic
				# If the command is "grant", and we already have a code, and it's valid, fail.
				# If the command is "grant", and there's no code (or it's invalid), proceed
				# If the command is "reset", and we don't already have a valid code, fail.
				# If the command is "reset", and we already have a valid code, proceed and replace it
				has_code = False
				if obj.access_code and obj.access_code.valid():
					has_code = True
				
				if cmd == 'accessgrant':
					if has_code:
						self.edit_success = False
						self.edit_error = 'quickedit_accesscode_exists'
					else:
						self.edit_success = obj.create_code(days, request=self.request)
						self.edit_error = 'quickedit_accesscode_grant'
				
				elif cmd == 'accessreset':
					if has_code:
						if is_int(target) and int(target) == obj.access_code.pk:
							obj.access_code.revoke()
							self.edit_success = obj.create_code(days, request=self.request)
							self.edit_error = 'quickedit_accesscode_grant'
						else:
							self.edit_success = False
							self.edit_error = 'quickedit_accesscode_id_invalid'
					else:
						self.edit_success = False
						self.edit_error = 'quickedit_accesscode_missing'
		
		elif cmd == 'accessrevoke':
			if is_int(target) and int(target) == obj.access_code.pk:
				obj.access_code.revoke()
				self.edit_success = True
			else:
				self.edit_success = False
				self.edit_error = 'quickedit_accesscode_id_invalid'
		
		else:
			self.edit_cmd_handled = False
	
	def get_object(self, queryset=None):
		obj = super(access_view, self).get_object(queryset)
		if not obj:
			raise Http404
		
		self.can_view, self.view_restriction = obj.can_view(self.request)
		if self.can_view:
			self.is_public, self.public_restriction = obj.is_public()
			self.can_edit, self.edit_restriction = obj.can_edit(self.request)
			
			if self.can_edit and self.request.GET.get('alitelvdi', False):
				# Handling this part with a separate method to make it easy to extend
				self.edit_object(obj)
		
		else:
			if self.view_restriction == 'access_404':
				self.request.session['deerfind_norecover'] = True
				raise Http404
			elif self.view_restriction == 'access_perms':
				raise PermissionDenied
			elif self.view_restriction != 'access_mature_prompt':
				# We need an object to be able to show the form correctly
				obj = None
		
		return obj
	
	def get_context_canview(self, context, **kwargs):
		"""Extendable method for context when permission checks for the object succeeded"""
		if not self.is_public:
			context['non_public'] = self.public_restriction
		
		if self.can_edit:
			context['can_edit'] = True
			if hasattr(context['object'], 'get_absolute_url'):
				context['return_to'] = context['object'].get_absolute_url()
			else:
				context['return_to'] = ''
		else:
			context['can_edit'] = False
		
		return context
	
	def get_context_restricted(self, context, **kwargs):
		"""Extendable method for context when permission checks for the object succeeded"""
		context['error'] = self.view_restriction
		if self.view_restriction == 'access_mature_prompt':
			if context['object']:
				context['title_page'] = "%s (Mature Content)" % str(context['object'])
			else:
				context['title_page'] = "Age Verification Required (Mature Content)"
			
			context['sitemeta_desc'] = "Viewing this content requires verifying your age, which will not be stored on our server in any way.  More details on the form, or in our Privacy Policy."
			context['embed_mature_form'] = True
		
		context['object'] = ''
		return context
	
	def get_context_data(self, **kwargs):
		context = super(access_view,self).get_context_data(**kwargs)
		
		# Permissions check already happened in get_object
		# But that also means we may or may not have an object
		# These usually go together, but we'll test both in case I screw something up
		if self.can_view and context['object']:
			return self.get_context_canview(context)
		
		else:
			# Either we can't view the object, or we don't have one
			# But to make extending this method easier, we won't remove the object until last
			context = self.get_context_restricted(context)
			context['object'] = ''
			return context
	
	def render_to_response(self, context, **response_kwargs):
		if self.can_edit and self.edit_success and self.edit_redirect_to is not None:
			# Operations that use object.quick_edit need a reload to reflect the changes
			return HttpResponseRedirect(self.edit_redirect_to)
		else:
			return super(access_view, self).render_to_response(context, **response_kwargs)
