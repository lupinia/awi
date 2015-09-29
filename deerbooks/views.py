#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.views import generic

from deerbooks.models import page, toc, export_file

class single_page(generic.DetailView):
	model=page
	
	def get_context_data(self, **kwargs):
		context=super(single_page,self).get_context_data(**kwargs)
		
		canview = context['page'].can_view(self.request)
		if not canview[0]:
			if canview[1] == 'access_404':
				from django.http import Http404
				self.request.session['deerfind_norecover'] = True
				raise Http404
			elif canview[1] == 'access_perms':
				from django.core.exceptions import PermissionDenied
				raise PermissionDenied
			else:
				context['page'] = ''
				context['error'] = canview[1]
		else:
			if context['page'].book_title:
				context['toc'] = context['page'].book_title.page_set.all().order_by('book_order')
			
			if context['page'].docfiles:
				context['docfiles'] = context['page'].docfiles.all().order_by('filetype')
			
		return context

class single_page_htm(single_page):
	template_name='deerbooks/page.html'

class single_page_txt(single_page):
	template_name='deerbooks/page.txt'
	content_type = 'text/plain'

class single_page_md(single_page):
	template_name='deerbooks/page.md'
	#content_type = 'text/markdown'			#	Temporarily switched to plain text MIME type for easier testing.
	content_type = 'text/plain'
	
class single_page_tex(single_page):
	template_name='deerbooks/page.tex'
	#content_type = 'application/x-tex'		#	Temporarily switched to plain text MIME type for easier testing.
	content_type = 'text/plain'


def finder(request):
	import os
	from django.core.urlresolvers import reverse
	return_data = (False,'')
	
	basename=os.path.basename(request.path)
	if '.' in basename:
		search_slug_list = basename.split('.')
		search_slug = search_slug_list[0]
		search_type = search_slug_list[1]
		
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
