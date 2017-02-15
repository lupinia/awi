#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.core.urlresolvers import reverse
from django.http import Http404
from django.views import generic

from awi_access.models import access_query
from deerbooks.models import page, toc, export_file
from deertrees.views import leaf_view
from sunset.utils import sunset_embed

class single_page(leaf_view):
	model=page
	
	def get_queryset(self, *args, **kwargs):
		return super(single_page, self).get_queryset(*args, **kwargs).select_related('book_title').prefetch_related('docfiles')
	
	def get_context_data(self, **kwargs):
		context=super(single_page,self).get_context_data(**kwargs)
		
		if context['object']:
			if context['object'].book_title:
				context['toc'] = context['object'].book_title.pages.filter(access_query(self.request)).select_related('cat').order_by('book_order')
			
			context['alt_version_exclude'] = []
			if context['object'].docfiles:
				context['docfiles'] = []
				for item in context['object'].docfiles.all():
					context['alt_version_exclude'].append(item.filetype)
					context['docfiles'].append(item)
			
			context['body_text'] = sunset_embed(context['object'].body, self.request)
			
			if self.request.GET.get('read', False):
				context['showcase_mode'] = True
			
			if context['can_edit']:
				context['edit_url'] = 'admin:deerbooks_page_change'
			
			context['extra_classes'] = 'writing_page'
		
		return context

class single_page_htm(single_page):
	template_name='deerbooks/page.html'

class single_page_txt(single_page):
	template_name='deerbooks/page.txt'
	content_type = 'text/plain; charset=utf-8'

class single_page_md(single_page):
	template_name='deerbooks/page.md'
	content_type = 'text/markdown; charset=utf-8'

class single_page_tex(single_page):
	template_name='deerbooks/page.tex'
	content_type = 'application/x-tex'


class book(generic.DetailView):
	model=toc
	
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
				page.body = sunset_embed(page.body, self.request)
				context['pages'].append(page)
				
				# source_url should be the url for the first visible page
				if not context['source_url']:
					context['source_url'] = 'http://%s%s' % (site_domain, reverse('page_htm', kwargs={'cached_url':page.cat.cached_url,'slug':page.slug,}))
				
				# timestamp should be the displayed timestamp of whichever page is newest
				cur_page_timestamp = page.display_times()
				if context['timestamp']:
					if context['timestamp'] < cur_page_timestamp[0]['timestamp']:
						context['timestamp'] = cur_page_timestamp[0]['timestamp']
				else:
					context['timestamp'] = cur_page_timestamp[0]['timestamp']
		
		if not context['pages']:
			raise Http404
		
		return context

class book_tex(book):
	template_name='deerbooks/book.tex'
	content_type = 'application/x-tex'

class book_txt(book):
	template_name='deerbooks/book.txt'
	content_type = 'text/plain; charset=utf-8'

class book_md(book):
	template_name='deerbooks/book.md'
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
		search_type = search_slug_list[-1]
		
		page_check = page.objects.filter(slug=search_slug)
		if page_check.exists():
			# Yay!  We found a match!  Let's make sure we can actually view it, though.
			access_check = page_check[0].can_view(request)
			if access_check[0]:
				# Ok cool, had to check your credentials!  It's just standard procedure, you know how it is around here.
				# Now let's figure out what type of URL to send back.
				# php, htm, and html are definitely a page object
				# pdf, dvi, ps, and epub are definitely an export_file object
				# txt, md, and tex could be either one
				is_page = ['php','htm','html','txt','md','tex']
				is_file = ['pdf','dvi','ps','epub','txt','md','tex']
				
				# Uploaded files take priority
				if search_type in is_file and not return_data[0]:
					check_files = page_check[0].docfiles.all()
					if check_files:
						for file in check_files:
							if file.filetype == search_type:
								return_data = (True,file.get_url())
								break
				
				# We didn't find it in the uploaded files, so maybe it's a page?
				if search_type in is_page and not return_data[0]:
					if search_type == 'php' or search_type == 'htm' or search_type == 'html':
						return_data = (True,reverse('page_htm',kwargs={'cached_url':page_check[0].cat.cached_url,'slug':page_check[0].slug}))
					elif search_type == 'txt':
						return_data = (True,reverse('page_txt',kwargs={'cached_url':page_check[0].cat.cached_url,'slug':page_check[0].slug}))
					elif search_type == 'md':
						return_data = (True,reverse('page_md',kwargs={'cached_url':page_check[0].cat.cached_url,'slug':page_check[0].slug}))
					elif search_type == 'tex':
						return_data = (True,reverse('page_tex',kwargs={'cached_url':page_check[0].cat.cached_url,'slug':page_check[0].slug}))
	
	return return_data
