#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

import re

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import DetailView

from awi.utils.errors import BadRequest
from awi_access.models import access_query
from deerbooks.models import page, toc
from deerfind.utils import urlpath
from deertrees.views import leaf_view
from sunset.utils import sunset_embed

class single_page(leaf_view):
	model = page
	alt_view = False
	disallowed_args = ['display', 'reply_to', 'mode']
	
	def dispatch(self, *args, **kwargs):
		# Stupid corner cases where stupid AI bots love to throw wrong query arguments at every URL
		for qarg in self.disallowed_args:
			if '%s=' % qarg in self.request.META.get('QUERY_STRING',''):
				raise BadRequest('invalid query argument (?%s=)' % qarg)
		
		return super(single_page,self).dispatch(*args, **kwargs)
	
	def get_queryset(self, *args, **kwargs):
		return super(single_page, self).get_queryset(*args, **kwargs).select_related('book_title').prefetch_related('docfiles')
	
	def get_context_data(self, **kwargs):
		context = super(single_page,self).get_context_data(**kwargs)
		context['has_reading_mode'] = True
		
		if self.alt_view and context.get('embed_mature_form') == True:
			raise PermissionDenied
		
		if context['object']:
			if context['object'].book_title:
				context['toc'] = context['object'].book_title.pages.filter(access_query(self.request)).select_related('cat').order_by('book_order')
			
			context['alt_version_exclude'] = []
			if context['object'].docfiles:
				context['docfiles'] = []
				for item in context['object'].docfiles.all():
					context['alt_version_exclude'].append(item.filetype)
					context['docfiles'].append(item)
			
			context['body_text'] = sunset_embed(context['object'].body_html, self.request)
			
			if self.request.GET.get('mode', False) == 'read':
				context['showcase_mode'] = True
			elif context['object'].showcase_default and self.request.GET.get('mode', False) != 'normal':
				context['showcase_mode'] = True
			else:
				context['showcase_mode'] = False
			
			if context['can_edit']:
				context['edit_url'] = 'admin:deerbooks_page_change'
			
			context['extra_classes'] = 'writing_page'
			context['external_links_wide'] = False
			
			context['sitemeta_desc'] = context['object'].summary_short
			if context['object'].revised:
				context['sitemeta_timestamp_mod'] = context['object'].timestamp_revised
			
			context['source_url'] =  context['object'].get_complete_url(self.request)
		
		return context

class single_page_htm(single_page):
	template_name = 'deerbooks/page.html'
	disallowed_args = ['display', 'reply_to']
	
	def get_context_data(self, **kwargs):
		context = super(single_page_htm,self).get_context_data(**kwargs)
		
		# Enable Highlight.js code highlighting, if needed
		regexp = re.compile(r'<pre(.*)><code')
		if regexp.search(context.get('body_text','')):
			context['highlight_code'] = True
		
		return context

class single_page_txt(single_page):
	template_name = 'deerbooks/page.txt'
	content_type = 'text/plain; charset=utf-8'
	alt_view = True

class single_page_md(single_page):
	template_name = 'deerbooks/page.md'
	content_type = 'text/markdown; charset=utf-8'
	alt_view = True

class single_page_tex(single_page):
	template_name = 'deerbooks/page.tex'
	content_type = 'application/x-tex'
	alt_view = True


class book(DetailView):
	model = toc
	alt_view = True
	
	def get_queryset(self, *args, **kwargs):
		return super(book, self).get_queryset(*args, **kwargs).prefetch_related('pages')
	
	def get_context_data(self, **kwargs):
		context=super(book,self).get_context_data(**kwargs)
		context['pages'] = []
		context['timestamp'] = False
		context['source_url'] = False
		
		# Prepping for the source_url
		if 'www' not in self.request.site.domain:
			site_domain = 'www.%s' % self.request.site.domain
		else:
			site_domain = self.request.site.domain
		
		for page in context['toc'].pages.filter(access_query()).order_by('book_order'):
			canview, view_restriction = page.can_view(self.request)
			if not canview:
				continue
			else:
				page.body = sunset_embed(page.body_html, self.request)
				context['pages'].append(page)
				
				# source_url should be the url for the first visible page
				if not context['source_url']:
					context['source_url'] =  page.get_complete_url(self.request)
				
				# timestamp should be the displayed timestamp of whichever page is newest
				cur_page_timestamp = page.display_times()
				if context['timestamp']:
					if context['timestamp'] < cur_page_timestamp[0]['timestamp']:
						context['timestamp'] = cur_page_timestamp[0]['timestamp']
				else:
					context['timestamp'] = cur_page_timestamp[0]['timestamp']
		
		if not context['pages']:
			self.request.session['deerfind_norecover'] = True
			raise Http404
		
		return context

class book_tex(book):
	template_name = 'deerbooks/book.tex'
	content_type = 'application/x-tex'

class book_txt(book):
	template_name = 'deerbooks/book.txt'
	content_type = 'text/plain; charset=utf-8'

class book_md(book):
	template_name = 'deerbooks/book.md'
	content_type = 'text/markdown; charset=utf-8'


def recent_widget(parent=False, parent_type=False, request=False):
	return_data = {'recent': [], 'featured': []}
	if parent_type == 'category' and parent:
		return_data['recent'] = page.objects.filter(cat__in=parent.get_descendants(include_self=True), published=True).filter(access_query(request)).exclude(featured=True).order_by('-timestamp_post').select_related('book_title','cat')[:4]
		return_data['featured'] = page.objects.filter(cat__in=parent.get_descendants(include_self=True), published=True, featured=True).filter(access_query(request)).order_by('-timestamp_post').select_related('book_title','cat')[:2]
		return return_data
	elif parent_type == 'tag' and parent:
		return_data['recent'] = page.objects.filter(tags=parent, published=True).filter(access_query(request)).exclude(featured=True).order_by('-timestamp_post').select_related('book_title','cat')[:4]
		return_data['featured'] = page.objects.filter(tags=parent, published=True, featured=True).filter(access_query(request)).order_by('-timestamp_post').select_related('book_title','cat')[:2]
		return return_data
	else:
		return False


def finder(request):
	is_found = False
	found_url = ''
	path = urlpath(request.path, force_lower=True)
	
	if path.is_file:
		# Only proceed if this path contains a filename
		page_check = page.objects.filter(basename__iexact=path.filename).select_related().prefetch_related('docfiles').first()
		if page_check:
			# Yay!  We found a match!  But can you view it?
			is_found = True
			perm_check, reason = page_check.can_view(request)
			if perm_check or reason == 'access_mature_prompt':
				# Yay!  We found a match that you're allowed to view!
				# Now let's figure out what type of URL to send back.
				# php, htm, and html are definitely a page object
				# pdf, dvi, ps, and epub are definitely an export_file object
				# txt, md, and tex could be either one
				is_page = ['php','htm','html','txt','md','tex']
				is_file = ['pdf','dvi','ps','epub','rtf','docx','txt','md','tex']
				
				# Uploaded files take priority
				if path.filetype in is_file:
					check_file = page_check.docfiles.filter(filetype=path.filetype).first()
					if check_file:
						found_url = check_file.get_url()
				
				# We didn't find it in the uploaded files, so maybe it's a page?
				if path.filetype in is_page and not found_url:
					if path.filetype == 'php' or path.filetype == 'html':
						search_type = 'htm'
					else:
						search_type = path.filetype
					
					found_url = reverse('page_%s' % search_type, kwargs={'cached_url':page_check.cat.cached_url, 'slug':page_check.basename})
	
	return (is_found, found_url)
