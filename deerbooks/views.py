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
				raise Http404
			elif canview[1] == 'access_perms':
				from django.core.exceptions import PermissionDenied
				raise PermissionDenied
			else:
				context['page'] = ''
				context['error'] = canview[1]
		else:
			if context['page'].book_title:
				context['toc'] = context['page'].book_title.page_set.all().order_by('page__book_order')
			
			if context['page'].docfiles:
				context['docfiles'] = context['page'].docfiles.all().order_by('filetype')
			
		return context

class single_page_htm(single_page):
	template_name='deerbooks/page.html'

class single_page_txt(single_page):
	template_name='deerbooks/page.txt'

class single_page_md(single_page):
	template_name='deerbooks/page.md'

class single_page_tex(single_page):
	template_name='deerbooks/page.tex'