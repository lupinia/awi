#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.module_loading import import_string
from django.views import generic

from awi_access.models import access_query
from deerconnect.models import contact_link
from deertrees.models import category, tag, leaf, special_feature
from sunset.utils import sunset_embed

class leaf_parent():
	template_name = 'deertrees/leaves.html'
	highlight_featured = True
	
	
	def get_leaves(self, parent=False, parent_type=False):
		blocks_main = settings.DEERTREES_BLOCKS
		leaf_filters = {}
		related_list = []
		prefetch_list = []
		
		for type, settings_dict in blocks_main.iteritems():
			if settings_dict.get('is_leaf',False):
				related_list.append(type)
				related_list.append('%s__cat' % type)
				related_list.append('%s__access_code' % type)
				
			if settings_dict.get('prefetch',False):
				for pf_field in settings_dict['prefetch']:
					prefetch_list.append('%s__%s' % (type, pf_field))
			
			if settings_dict.get('related',False):
				for sr_field in settings_dict['related']:
					related_list.append('%s__%s' % (type, sr_field))
		
		leaf_ordering = ['-featured','-timestamp_post']
		leaf_filters['timestamp_post__lte'] = timezone.now()
		
		# Special cases
		# Site home
		if parent_type == 'homepage':
			leaf_ordering = ['-timestamp_post',]
			leaf_filters['featured'] = True
		elif parent_type == 'main_feed':
			leaf_ordering = ['-timestamp_post',]
		elif parent_type == 'category' and parent:
			leaf_filters['cat'] = parent
		elif parent_type == 'tag' and parent:
			leaf_filters['tags'] = parent
		elif parent_type == 'root' and parent:
			descendants = parent.get_descendants()
			self.highlight_featured = False
			leaf_ordering = ['-timestamp_post',]
			leaf_filters['featured'] = True
			leaf_filters['cat__in'] = descendants
		
		leaves = leaf.objects.select_related(*related_list).prefetch_related(*prefetch_list).filter(**leaf_filters).filter(access_query(self.request)).order_by(*leaf_ordering)
		
		if leaves:
			return leaves
		else:
			return False
	
	def assemble_blocks(self, parent=False, parent_type=False, view_type='default'):
		# BLOCK OPTIONS (in order of assignment)
		# main:  Main content area.  There's only one of these.
		# main_left:  Left side of a vertically split main block.
		# main_right:  Right side of a vertically split main block.
		# sidebar:  Narrow column along the right side of the page.  Can contain infinite blocks.
		# main_2:  A second main content area.  Rarely used, but it's an option.
		
		blocks_main = settings.DEERTREES_BLOCKS
		blocks_special = settings.DEERTREES_BLOCKS_SPECIAL
		blocks_map = settings.DEERTREES_BLOCK_MAP
		
		leaf_content = {}
		leaf_count = {}
		assigned_to_blocks = []
		returned_data = [False,{}]
		
		map = blocks_map.get(view_type, False)
		if not map:
			view_type='default'
			map = blocks_map['default']
		
		# These have to be in a specific order, so map.keys() doesn't work reliably.
		blocks_to_assign_raw = ['main','main_left','main_right','sidebar','main_2']
		blocks_to_assign = []
		for blockname in blocks_to_assign_raw:
			if map.get(blockname,False) and map.get(blockname,False) != 'meta':
				blocks_to_assign.append(blockname)
		
		leaves = self.get_leaves(parent,parent_type)
		if leaves:
			#	Loop all of our leaves, and store them in the correct dictionary elements
			for leaf_item in leaves:
				type = leaf_item.type
				if not leaf_content.get(type,False):
					leaf_content[type] = []
					leaf_count[type] = 0
				
				# Pagination counter check should go here.
				if not blocks_main.get(type,{}).get('count',0) or leaf_count.get(type,0) <= blocks_main.get(type,{}).get('count',50):
					leaf_data = getattr(leaf_item,type,None)
					if leaf_data:
						leaf_content[type].append(leaf_data)
						leaf_count[type] = leaf_count[type] + 1
		
		for block in blocks_to_assign:
			if map.get(block,False) == 'desc':
				returned_data[1][block] = ['desc',]
				returned_data[1]['desc_in_block'] = True
			else:
				# If we're here, we need to put some content in this block.
				# Check the special cases first, then check the leaves.
				block_is_complete = False
				returned_data[1][block] = []
				
				for type in map.get(block,False):
					block_contents = False
					if type not in assigned_to_blocks and not block_is_complete:
						if blocks_special.get(type,False):
							# This is a special block; import its function from somewhere else and run it.
							special_function_name = blocks_special.get(type,{}).get('custom_obj', False)
							if special_function_name:
								special_function = import_string(special_function_name)
								block_contents = {
									'type':type, 
									'title':blocks_special.get(type,{}).get('title',False),
									'data':special_function(parent, parent_type, self.request), 
									'template':blocks_special.get(type,{}).get('template',False),
								}
						
						elif leaf_content.get(type,False):
							# This is a leaf, and we have data for it.
							block_contents = leaf_content.get(type,False)
							block_contents = {
								'type':type, 
								'title':blocks_main.get(type,{}).get('title',False),
								'data':leaf_content.get(type,False), 
								'template':blocks_main.get(type,{}).get('template',False),
							}
						
						if block_contents and block_contents.get('data',False):
							returned_data[1][block].append(block_contents)
							returned_data[0] = True
							assigned_to_blocks.append(type)
							
							# Sidebar is a special case where we're not limited to just one block.
							if block != 'sidebar':
								block_is_complete = True
		
		return returned_data


class homepage(leaf_parent, generic.TemplateView):
	highlight_featured = False
	
	def get_context_data(self, **kwargs):
		context = super(homepage,self).get_context_data(**kwargs)
		context['highlight_featured'] = self.highlight_featured
		context['homepage'] = True
		
		blocks = self.assemble_blocks(parent_type = 'homepage', view_type='home')
		if blocks[0]:
			context.update(blocks[1])
		
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
		#	This handles the edge case of a multiroot G2 URL that's not rewritten
		#	For example, /photo/?g2_itemId=2289
		#	All other contingencies (full ".php?g2_itemId=" URL, shortened .g2 URL) are handled elsewhere.
		if 'g2_itemId' in self.request.META.get('QUERY_STRING',''):
			raise Http404
		else:
			return super(category_list,self).dispatch(*args, **kwargs)
	
	def get_queryset(self, *args, **kwargs):
		return super(category_list, self).get_queryset(*args, **kwargs).select_related('background_tag', 'access_code')
	
	def get_context_data(self, **kwargs):
		context = super(category_list,self).get_context_data(**kwargs)
		
		canview = context['object'].can_view(self.request)
		if not canview[0]:
			if canview[1] == 'access_404':
				self.request.session['deerfind_norecover'] = True
				raise Http404
			elif canview[1] == 'access_perms':
				raise PermissionDenied
			elif canview[1] == 'access_mature_prompt':
				context['error'] = canview[1]
				context['object'] = ''
				context['embed_mature_form'] = True
			else:
				context['object'] = ''
				context['error'] = canview[1]
		else:
			if context['object'].can_edit(self.request)[0]:
				context['return_to'] = context['object'].get_absolute_url()
				context['can_edit'] = True
				context['edit_mode'] = 'cat'
				
				if self.request.GET.get('feature', False) and not context['object'].featured:
					context['object'].featured = True
					context['object'].save()
				elif self.request.GET.get('unfeature', False) and context['object'].featured:
					context['object'].featured = False
					context['object'].save()
				elif self.request.GET.get('publish', False) and not context['object'].published:
					context['object'].published = True
					context['object'].save()
				elif self.request.GET.get('unpublish', False) and context['object'].published:
					context['object'].published = False
					context['object'].save()
				elif self.request.GET.get('change_cat', False):
					new_cat = get_object_or_404(category, pk=self.request.GET.get('change_cat'))
					context['object'].parent = new_cat
					context['object'].save()
			else:
				context['can_edit'] = False
			
			blocks = self.assemble_blocks(context['object'],'category',context['object'].view_type)
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
			
			if context['object'].desc:
				context['body_text'] = sunset_embed(context['object'].desc, self.request)
			else:
				context['body_text'] = context['object'].summary
		
		return context


class tag_list(leaf_parent, generic.DetailView):
	model=tag
	
	def get_context_data(self, **kwargs):
		context = super(tag_list,self).get_context_data(**kwargs)
		context['highlight_featured'] = self.highlight_featured
		if context['object'].can_edit(self.request)[0]:
			context['return_to'] = context['object'].get_absolute_url()
			context['can_edit'] = True
			context['edit_mode'] = 'tags'
		
		blocks = self.assemble_blocks(context['object'],'tag',context['object'].view_type)
		if blocks[0]:
			context.update(blocks[1])
		else:
			context['error'] = 'tag_empty'
		
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		context['breadcrumbs'].append({'url':reverse('all_tags'), 'title':'Tags'})
		context['breadcrumbs'].append({'url':reverse('tag',kwargs={'slug':context['object'].slug,}), 'title':context['object'].title})
		
		if context['object'].desc:
			context['body_text'] = context['object'].desc
		
		return context


class all_tags(generic.TemplateView):
	template_name='deertrees/taglist.html'
	
	def get_context_data(self, **kwargs):
		context = super(all_tags,self).get_context_data(**kwargs)
		
		# TODO:  Filter by sitemap_include and hide empty tags if not return_to
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


#	Helper functions imported by other views
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


def subcats(parent=False, parent_type=False, request=False):
	if parent_type == 'category' and parent:
		child_cats = parent.children.filter(access_query(request)).order_by('title').select_related('icon')
		if child_cats:
			return child_cats
		else:
			return False
	else:
		return False


class leaf_view(generic.DetailView):
	def get_queryset(self, *args, **kwargs):
		return super(leaf_view, self).get_queryset(*args, **kwargs).select_related('access_code','cat').prefetch_related('tags')
	
	def check_int(self, check):
		try:
			int_test = int(check)
			return True
		except ValueError:
			return False
	
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
			elif canview[1] == 'access_mature_prompt':
				context['error'] = canview[1]
				context['object'] = ''
				context['embed_mature_form'] = True
			else:
				context['object'] = ''
				context['error'] = canview[1]
		else:
			# Tags
			context['tags'] = context['object'].tags.all()
			context['category'] = context['object'].cat
			
			# Editing Functions
			if context['object'].can_edit(self.request)[0]:
				context['return_to'] = context['object'].get_absolute_url()
				context['can_edit'] = True
				changed = False
				
				# DeerTrees Leaf commands
				if self.request.GET.get('add_tag', False):
					if self.check_int(self.request.GET.get('add_tag', False)):
						new_tag = get_object_or_404(tag, pk=self.request.GET.get('add_tag'))
						context['object'].tags.add(new_tag)
						context['object'].save()
						changed = True
				elif self.request.GET.get('remove_tag', False):
					if self.check_int(self.request.GET.get('remove_tag', False)):
						old_tag = get_object_or_404(tag, pk=self.request.GET.get('remove_tag'))
						context['object'].tags.remove(old_tag)
						context['object'].save()
						changed = True
				elif self.request.GET.get('change_cat', False):
					if self.check_int(self.request.GET.get('change_cat', False)):
						new_cat = get_object_or_404(category, pk=self.request.GET.get('change_cat'))
						context['object'].cat = new_cat
						context['object'].save()
						changed = True
				
				# Awi Access commands
				elif self.request.GET.get('feature', False) and not context['object'].featured:
					context['object'].featured = True
					context['object'].save()
					changed = True
				elif self.request.GET.get('unfeature', False) and context['object'].featured:
					context['object'].featured = False
					context['object'].save()
					changed = True
				elif self.request.GET.get('publish', False) and not context['object'].published:
					context['object'].published = True
					context['object'].save()
					changed = True
				elif self.request.GET.get('unpublish', False) and context['object'].published:
					context['object'].published = False
					context['object'].save()
					changed = True
				
				# Awi Access access code commands
				elif self.request.GET.get('revoke_code', False) and context['object'].access_code:
					if self.check_int(self.request.GET.get('revoke_code', False)) and int(self.request.GET.get('revoke_code', False)) == context['object'].access_code.pk:
						context['object'].access_code.is_valid = False
						context['object'].access_code.save()
						changed = True
				elif self.request.GET.get('new_access_code', False) and self.request.user == context['object'].owner:
					if self.request.GET.get('new_access_code', False) == 'permanent':
						new_age = None
					else:
						new_age = self.request.GET.get('new_access_code', False)
					
					if new_age is None or self.check_int(new_age):
						if new_age is not None:
							new_age = int(new_age)
						
						if context['object'].access_code and context['object'].access_code.valid() and self.check_int(self.request.GET.get('replace', False)) and int(self.request.GET.get('replace', False)) == context['object'].access_code.pk:
							context['object'].access_code.is_valid = False
							context['object'].access_code.save()
							context['object'].create_code(age=new_age, request=self.request)
							changed = True
						elif not context['object'].access_code or not context['object'].access_code.valid():
							context['object'].create_code(age=new_age, request=self.request)
							changed = True
				
				if changed:
					# I'm annoyed that there isn't an easier/more reliable way to do this.
					cache.clear()
			
			else:
				context['return_to'] = ''
				context['can_edit'] = False
			
			# Breadcrumbs
			ancestors = context['object'].cat.get_ancestors(include_self=True)
			if not context.get('breadcrumbs',False):
				context['breadcrumbs'] = []
			
			for crumb in ancestors:
				context['breadcrumbs'].append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
			
			context['breadcrumbs'].append({'url':context['object'].get_absolute_url(), 'title':str(context['object'])})
		
		return context


class special_feature_view():
	leaf = None
	
	def get_leaf(self, **kwargs):
		if self.kwargs.get('special_feature_slug', False):
			self.leaf = get_object_or_404(special_feature.objects.select_related(), url=self.kwargs.get('special_feature_slug', False))
			return True
		else:
			return False
	
	def breadcrumbs(self, **kwargs):
		breadcrumbs = []
		if not self.leaf:
			self.get_leaf()
		
		if self.leaf:
			ancestors = self.leaf.cat.get_ancestors(include_self=True)
			
			for crumb in ancestors:
				breadcrumbs.append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
			
			breadcrumbs.append({'url':u'%s%s/' % (reverse('category',kwargs={'cached_url':self.leaf.cat.cached_url,}),self.leaf.url), 'title':self.leaf.title})
			
			return breadcrumbs
		
		else:
			return False


#	Views that don't use the leaf system.
class all_cats(generic.TemplateView, special_feature_view):
	template_name = 'deertrees/sitemap.html'
	
	def get_context_data(self, **kwargs):
		context = super(all_cats,self).get_context_data(**kwargs)
		context['view'] = 'catlist'
		context['cats'] = category.objects.filter(access_query(self.request)).annotate(num_leaves=Count('leaf'))
		context['breadcrumbs'] = self.breadcrumbs()
		
		if self.request.GET.get('return_to') and self.request.user.has_perm('deertrees.change_leaf'):
			context['return_to'] = self.request.GET.get('return_to')
		
		return context


class sitemap(all_cats):
	template_name = 'deertrees/sitemap.html'
	
	def get_context_data(self, **kwargs):
		context = super(sitemap,self).get_context_data(**kwargs)
		context['view'] = 'sitemap'
		context['cats'] = context['cats'].filter(sitemap_include=True)
		context['tags'] = tag.objects.filter(sitemap_include=True).annotate(num_leaves=Count('leaf'))
		return context
