#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from collections import OrderedDict
from itertools import cycle

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import generic

from awi_access.models import access_query
from deerconnect.models import contact_link
from deertrees.models import category, tag, leaf

class leaf_parent():
	template_name = 'deertrees/leaves.html'
	highlight_featured = True
	
	def get_leaves(self, parent=False, parent_type=False):
		leaf_filters = {}
		blocks_map = settings.DEERTREES_BLOCKS
		leaf_list = []
		for type, settings_dict in blocks_map.iteritems():
			if settings_dict.get('is_leaf',False):
				leaf_list.append(type)
				leaf_list.append('%s__cat' % type)
		
		leaf_ordering = ['-featured','-timestamp_post']
		leaf_filters['timestamp_post__lte'] = timezone.now()
		
		if parent_type == 'homepage':
			leaf_ordering = ['-timestamp_post',]
			leaf_filters['featured'] = True
		elif parent_type == 'main_feed':
			leaf_ordering = ['-timestamp_post',]
		elif parent_type == 'category' and parent:
			leaf_filters['cat'] = parent
		elif parent_type == 'tag' and parent:
			leaf_filters['tags'] = parent
		
		leaves = leaf.objects.select_related(*leaf_list).filter(**leaf_filters).filter(access_query(self.request)).order_by(*leaf_ordering)
		
		if leaves:
			return leaves
		else:
			if parent_type == 'category' and parent:
				descendants = parent.get_descendants()
				leaves = leaf.objects.select_related(*leaf_list).filter(featured=True, cat__in=descendants).filter(access_query(self.request)).order_by('-timestamp_post')
				if leaves:
					self.highlight_featured = False
					return leaves
				else:
					return False
			else:
				return False
	
	def assemble_blocks(self, parent=False, parent_type=False):
		#	BLOCK STRUCTURE
		#	In order of assignment
		#	
		#	main_full_1	- Primary content area, full-width.  Omitted if content_priority is desc
		#	sidebar		- List; add two, then go to main_full_2 if needed.
		#	main_full_2	- Secondary content area, full_width.
		#	sidebar		- List; do one, then go to a main_half block, and alternate as-needed.
		#	main_half - List; there can be as many of these as needed.  Alternate as-needed with sidebar.
		
		blocks_map = settings.DEERTREES_BLOCKS
		blocks = {}
		blocks_count = {}
		assigned_to_blocks = []
		returned_data = [False,{}]
		
		#	Build the list of blocks to assign
		if parent_type == 'homepage':
			blocks_to_assign = ['main_half','sidebar','main_half','sidebar']
		else:
			blocks_to_assign = ['sidebar','sidebar','main_full_2']
			if parent and parent.content_priority != 'desc':
				blocks_to_assign.insert(0,'main_full_1')
		
		#	Loop the known-existing content types, to get a list.  We'll deal with priority later.
		for type, settings_dict in blocks_map.iteritems():
			blocks[type] = []
			blocks_count[type] = 0
		
		#	Content time!
		#	First, check for subcategories and contact links
		if parent_type == 'category' and parent:
			child_cats = parent.children.filter(access_query(self.request)).order_by('title')
			if child_cats:
				blocks['category'] = child_cats
			
			ancestors = parent.get_ancestors(include_self=True)
			contact_links = contact_link.objects.filter(cat__in=ancestors).filter(access_query(self.request)).order_by('-timestamp_mod')
			if contact_links:
				blocks['contact_link'] = contact_links
		
		#	Now get items in this category
		leaves = self.get_leaves(parent,parent_type)
		if leaves:
			#	1.  Loop all of our leaves
			#	2.  For each leaf, loop blocks_map to find its type
			#	3.  Once that check is successful, put it in the correct block dictionary
			for leaf_item in leaves:
				for type, blocksettings in blocks_map.iteritems():
					if blocksettings['is_leaf']:
						if blocks_count[type] <= 50:
							leaf_content = getattr(leaf_item,type,None)
							if leaf_content:
								blocks[type].append(leaf_content)
								blocks_count[type] += 1
		
		#	Clean up empty elements
		empty_keys = [k for k,v in blocks.iteritems() if not v]
		for k in empty_keys:
			del blocks[k]
		
		#	Moment of truth!  Did we actually get anything out of this category?
		if blocks:
			returned_data[0] = True
			
			#	Ok, we how have all of our leaves neatly arranged by type and ready to display.
			#	Now it's time to assign blocks for display
			#	Assignment time!
			#	Start with the special case
			if blocks_to_assign[0] == 'main_full_1' and blocks.get(parent.content_priority,False):
				returned_data[1]['main_full_1'] = {'type':parent.content_priority,'title':blocks_map[parent.content_priority]['title'],'data':blocks[parent.content_priority],'template':blocks_map[parent.content_priority]['template']}
				blocks_to_assign.pop(0)
				blocks.pop(parent.content_priority)
			
			#	Make sure we didn't just pop off the last/only one.
			if blocks:
				order_main = {}
				order_sidebar = {}
				blockorder_main = False
				blockorder_sidebar = False
				
				#	Now, let's build a priority list per region
				for type, content in blocks.iteritems():
					if blocks_map[type].get('main',False):
						order_main[str(blocks_map[type]['main'])] = {'type':type,'title':blocks_map[type]['title'],'data':content,'template':blocks_map[type]['template']}
					if blocks_map[type].get('sidebar',False):
						order_sidebar[str(blocks_map[type]['sidebar'])] = {'type':type,'title':blocks_map[type]['title'],'data':content,'template':blocks_map[type]['template']}
				
				#	And now put them in order
				if order_main:
					blockorder_main = []
					for key,value in sorted(order_main.iteritems()):
						blockorder_main.append(value)
					
				if order_sidebar:
					blockorder_sidebar = []
					for key,value in sorted(order_sidebar.iteritems()):
						blockorder_sidebar.append(value)
				
				#	Assign the main blocks first 
				for blockname in blocks_to_assign:
					if 'main' in blockname and blockorder_main:
						for blockdata in blockorder_main:
							if blockdata['type'] not in assigned_to_blocks:
								if not returned_data[1].get('main_half',False):
									returned_data[1]['main_half'] = []
								
								if blockname == 'main_half':
									returned_data[1]['main_half'].append(blockdata)
								else:
									returned_data[1][blockname] = blockdata
								assigned_to_blocks.append(blockdata['type'])
								break
					
					elif 'sidebar' in blockname and blockorder_sidebar:
						for blockdata in blockorder_sidebar:
							if blockdata['type'] not in assigned_to_blocks:
								if not returned_data[1].get('sidebar',False):
									returned_data[1]['sidebar'] = []
								returned_data[1]['sidebar'].append(blockdata)
								assigned_to_blocks.append(blockdata['type'])
								break
				
				#	Quick bit of cleanup
				for content_type in assigned_to_blocks:
					blocks.pop(content_type,None)
				
				#	Is there anything left?
				if blocks:
					#	Seriously?  Ok then, we'll just go through whatever's left.
					#	Sidebar takes priority.
					for sidebar_data in blockorder_sidebar:
						if sidebar_data['type'] not in assigned_to_blocks:
							returned_data[1]['sidebar'].append(sidebar_data)
							assigned_to_blocks.append(sidebar_data['type'])
					
					for main_data in blockorder_main:
						if main_data['type'] not in assigned_to_blocks:
							if not returned_data[1]['main_half']:
								returned_data[1]['main_half'] = []
							returned_data[1]['main_half'].append(main_data)
							assigned_to_blocks.append(main_data['type'])
		
		return returned_data


class homepage(leaf_parent, generic.TemplateView):
	highlight_featured = False
	
	def get_context_data(self, **kwargs):
		context = super(homepage,self).get_context_data(**kwargs)
		context['highlight_featured'] = self.highlight_featured
		context['homepage'] = True
		
		blocks = self.assemble_blocks(parent_type = 'homepage')
		if blocks[0]:
			context.update(blocks[1])
		
		return context

class sitemap(generic.TemplateView):
	template_name = 'deertrees/sitemap.html'
	
	def get_context_data(self, **kwargs):
		context = super(sitemap,self).get_context_data(**kwargs)
		
		context['tags'] = tag.objects.all().annotate(num_leaves=Count('leaf'))
		context['cats'] = category.objects.filter(access_query(self.request)).annotate(num_leaves=Count('leaf'))
		
		return context


class main_rssfeed(leaf_parent, generic.TemplateView):
	template_name='deertrees/rss.xml'
	
	def get_context_data(self, **kwargs):
		context = super(main_rssfeed,self).get_context_data(**kwargs)
		context['highlight_featured'] = self.highlight_featured
		
		leaves = self.get_leaves(parent_type = 'main_feed')
		if leaves:
			context['leaves'] = leaves[:30]
		else:
			context['error'] = 'feed_empty'
		
		return context

class category_list(leaf_parent, generic.DetailView):
	model=category
	slug_field='cached_url'
	slug_url_kwarg='cached_url'
	
	def dispatch(self, *args, **kwargs):
		#	This is where our handler for special-case G2 compatibility will go
		#	This handles the edge case of a multiroot URL that's not rewritten
		#	For example, /photo/?g2_itemId=2289
		#	All other contingencies (full ".php?g2_itemId=" URL, shortened .g2 URL) are handled elsewhere.
		if 'g2_itemId' in self.request.META.get('QUERY_STRING',''):
			from django.http import Http404
			raise Http404
		else:
			return super(category_list,self).dispatch(*args, **kwargs)
	
	def get_context_data(self, **kwargs):
		context = super(category_list,self).get_context_data(**kwargs)
		
		blocks = self.assemble_blocks(context['object'],'category')
		if blocks[0]:
			context.update(blocks[1])
		else:
			context['error'] = 'cat_empty'
		
		ancestors = context['object'].get_ancestors(include_self=True)
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		for crumb in ancestors:
			context['breadcrumbs'].append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
		
		context['highlight_featured'] = self.highlight_featured
		return context

class tag_list(leaf_parent, generic.DetailView):
	model=tag
	
	def get_context_data(self, **kwargs):
		context = super(tag_list,self).get_context_data(**kwargs)
		context['highlight_featured'] = self.highlight_featured
		
		blocks = self.assemble_blocks(context['object'],'tag')
		if blocks[0]:
			context.update(blocks[1])
		else:
			context['error'] = 'tag_empty'
		
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		context['breadcrumbs'].append({'url':reverse('all_tags'), 'title':'Tags'})
		context['breadcrumbs'].append({'url':reverse('tag',kwargs={'slug':context['object'].slug,}), 'title':context['object'].title})
		
		return context

class all_tags(generic.TemplateView):
	template_name='deertrees/taglist.html'
	
	def get_context_data(self, **kwargs):
		context = super(all_tags,self).get_context_data(**kwargs)
		
		tag_list = tag.objects.all().order_by('title')
		if tag_list:
			context['tags'] = tag_list
		else:
			context['error'] = 'no_tags'
		
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		context['breadcrumbs'].append({'url':reverse('all_tags'), 'title':'Tags'})
		
		if self.request.GET.get('return_to') and self.request.user.has_perm('deertrees.change_leaf'):
			context['return_to'] = self.request.GET.get('return_to')
		
		return context

class leaf_view(generic.DetailView):
	def get_context_data(self, **kwargs):
		context=super(leaf_view,self).get_context_data(**kwargs)
		
		# Permissions check
		canview = context['object'].can_view(self.request)
		if not canview[0]:
			if canview[1] == 'access_404':
				self.request.session['deerfind_norecover'] = True
				raise Http404
			elif canview[1] == 'access_perms':
				from django.core.exceptions import PermissionDenied
				raise PermissionDenied
			else:
				context['object'] = ''
				context['error'] = canview[1]
		else:
			# Tags
			context['tags'] = context['object'].tags.all()
			
			# Adding/Removing Tags
			if self.request.user.has_perm('deertrees.change_leaf'):
				context['can_edit_tags'] = True
				context['return_to'] = context['object'].get_absolute_url()
				
				if self.request.GET.get('add_tag'):
					new_tag = get_object_or_404(tag, pk=self.request.GET.get('add_tag'))
					context['object'].tags.add(new_tag)
					context['object'].save()
				elif self.request.GET.get('remove_tag'):
					old_tag = get_object_or_404(tag, pk=self.request.GET.get('remove_tag'))
					context['object'].tags.remove(old_tag)
					context['object'].save()
			else:
				context['can_edit_tags'] = False
				context['return_to'] = ''
			
			# Breadcrumbs
			ancestors = context['object'].cat.get_ancestors(include_self=True)
			if not context.get('breadcrumbs',False):
				context['breadcrumbs'] = []
			
			for crumb in ancestors:
				context['breadcrumbs'].append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
			
			context['breadcrumbs'].append({'url':context['object'].get_absolute_url(), 'title':str(context['object'])})
			
		return context

def finder(request):
	import os
	return_data = (False,'')
	
	#	Fix the trailing slash
	if request.path.endswith('/'):
		basename=os.path.basename(request.path[:-1])
	else:
		basename=os.path.basename(request.path)
	
	if '.' in basename:
		#	Categories don't have dots in the slug
		return return_data
	else:
		cat_check = category.objects.filter(slug=basename)
		if cat_check.exists():
			access_check = cat_check[0].can_view(request)
			if access_check[0]:
				return_data = (True,reverse('category',kwargs={'cached_url':cat_check[0].cached_url,}))
	
	return return_data
