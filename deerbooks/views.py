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
from django.views import generic

from awi_access.models import access_query
from deerbooks.models import page, toc, export_file
from deertrees.views import leaf_view
from sunset.utils import sunset_embed

class single_page(leaf_view):
	model = page
	alt_view = False
	
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
			
			context['sitemeta_desc'] = context['object'].summary_short
			if context['object'].revised:
				context['sitemeta_timestamp_mod'] = context['object'].timestamp_revised
			
			context['source_url'] =  context['object'].get_complete_url(self.request)
		
		return context

class single_page_htm(single_page):
	template_name = 'deerbooks/page.html'
	
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


class book(generic.DetailView):
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
			canview = page.can_view(self.request)
			if not canview[0]:
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
	import os
	return_data = (False,'')
	
	basename=os.path.basename(request.path)
	if '.' in basename:
		search_slug_list = basename.split('.')
		search_slug = search_slug_list[0]
		search_type = search_slug_list[-1].lower()
		
		page_check = page.objects.filter(slug__iexact=search_slug).filter(access_query(request)).select_related().prefetch_related('docfiles').first()
		if page_check:
			# Yay!  We found a match that you're allowed to view!
			# Now let's figure out what type of URL to send back.
			# php, htm, and html are definitely a page object
			# pdf, dvi, ps, and epub are definitely an export_file object
			# txt, md, and tex could be either one
			is_page = ['php','htm','html','txt','md','tex']
			is_file = ['pdf','dvi','ps','epub','rtf','docx','txt','md','tex']
			
			# Uploaded files take priority
			if search_type in is_file and not return_data[0]:
				check_file = page_check.docfiles.filter(filetype=search_type).first()
				if check_file:
					return_data = (True, check_file.get_url())
			
			# We didn't find it in the uploaded files, so maybe it's a page?
			if search_type in is_page and not return_data[0]:
				if search_type == 'php' or search_type == 'html':
					search_type = 'htm'
				
				return_data = (True,reverse('page_%s' % search_type, kwargs={'cached_url':page_check.cat.cached_url, 'slug':page_check.slug}))
	
	return return_data
