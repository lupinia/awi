#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Case, Count, IntegerField, Sum, When
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.module_loading import import_string
from django.views.generic import DetailView, ListView, TemplateView

from awi.utils.errors import BadRequest
from awi.utils.types import is_int
from awi_access.models import access_query
from awi_access.views import access_view
from deerfind.utils import g2_lookup, urlpath
from deertrees.models import category, tag, leaf, special_feature
from sunset.utils import sunset_embed

class leaf_parent():
	template_name = 'deertrees/leaves.html'
	highlight_featured = True
	
	def get_leaves(self, parent=False, parent_type=False, is_feed=False):
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
		# RSS feed (Home)
		elif parent_type == 'main_feed':
			leaf_ordering = ['-timestamp_post',]
		# 
		elif parent_type == 'category' and parent:
			if is_feed:
				leaf_filters['cat__in'] = parent.get_descendants(include_self=True).filter(access_query(getattr(self, 'request', False)))
			else:
				leaf_filters['cat'] = parent
		elif parent_type == 'tag' and parent:
			leaf_filters['tags'] = parent
		elif parent_type == 'root' and parent:
			descendants = parent.get_descendants().filter(access_query(getattr(self, 'request', False)))
			self.highlight_featured = False
			leaf_ordering = ['-timestamp_post',]
			leaf_filters['featured'] = True
			leaf_filters['cat__in'] = descendants
		
		if is_feed:
			leaf_ordering = ['-timestamp_post',]
			prefetch_list.append('tags')
		
		leaves = leaf.objects.select_related(*related_list).prefetch_related(*prefetch_list).filter(**leaf_filters).filter(access_query(getattr(self, 'request', False))).order_by(*leaf_ordering)
		
		if leaves or is_feed:
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
		block_output = {}
		has_blocks = False
		
		map = blocks_map.get(view_type, False)
		if not map:
			view_type='default'
			map = blocks_map['default']
		
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
					leaf_data = getattr(leaf_item, type, None)
					if leaf_data:
						leaf_content[type].append(leaf_data)
						leaf_count[type] = leaf_count[type] + 1
		
		for block in blocks_to_assign:
			if map.get(block,False) == 'desc':
				block_output[block] = ['desc',]
				block_output['desc_in_block'] = True
			else:
				# If we're here, we need to put some content in this block.
				# Check the special cases first, then check the leaves.
				block_is_complete = False
				block_output[block] = []
				
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
							block_output[block].append(block_contents)
							has_blocks = True
							assigned_to_blocks.append(type)
							
							# Sidebar is a special case where we're not limited to just one block.
							if block != 'sidebar':
								block_is_complete = True
		
		return (has_blocks, block_output)


class homepage(leaf_parent, TemplateView):
	highlight_featured = False
	
	def dispatch(self, *args, **kwargs):
		# Stupid corner cases where stupid AI bots love to throw wrong query arguments at every URL
		if 'mode=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?mode=)')
		elif 'display=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?display=)')
		elif 'reply_to=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?reply_to=)')
		
		return super(homepage,self).dispatch(*args, **kwargs)
	
	def get_context_data(self, **kwargs):
		context = super(homepage,self).get_context_data(**kwargs)
		context['highlight_featured'] = self.highlight_featured
		context['homepage'] = True
		context['rss_feed'] = True
		
		blocks = self.assemble_blocks(parent_type = 'homepage', view_type='home')
		if blocks[0]:
			context.update(blocks[1])
		
		context['title_site'] = '' # This will force default to the full homepage title
		context['title_page'] = '' # This will force default to the full homepage title
		
		return context


class category_list(leaf_parent, access_view):
	model = category
	slug_field = 'cached_url'
	slug_url_kwarg = 'cached_url'
	g2redir = None
	
	def dispatch(self, *args, **kwargs):
		#	This handles the edge case of a multiroot G2 URL that's not rewritten
		#	For example, /photo/?g2_itemId=2289
		#	All other contingencies (full ".php?g2_itemId=" URL, shortened .g2 URL) are handled elsewhere.
		if 'g2_itemId' in self.request.META.get('QUERY_STRING',''):
			g2url, g2results = g2_lookup(self.request.GET.get('g2_itemId', 0), self.request)
			if g2url:
				if g2results == 'found_cat':
					# Corner case: If the G2 ID points here, avoid a circular redirect
					self.g2redir = g2url
				else:
					self.request.session['deerfind_path'] = g2url
					raise Http404
			elif g2results == 'retracted' or g2results == 'access_404':
				self.request.session['deerfind_norecover'] = True
				raise Http404
		
		# Stupid corner cases where stupid AI bots love to throw wrong query arguments at every URL
		if 'mode=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?mode=)')
		elif 'display=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?display=)')
		elif 'reply_to=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?reply_to=)')
		
		return super(category_list,self).dispatch(*args, **kwargs)
	
	def edit_object(self, obj):
		super(category_list, self).edit_object(obj)
		
		if not self.edit_cmd_handled:
			self.edit_cmd_handled = True
			# Pull known arguments
			cmd = self.request.GET.get('alitelvdi', '')
			target = self.request.GET.get('diyosdi', None)
			
			if cmd == 'mv':
				# Move to a different parent directory (category)
				# Requires diyosdi (target) parameter
				if target and is_int(target):
					self.request.session['deerfind_norecover'] = True
					dest = get_object_or_404(category, pk=int(target))
					self.request.session['deerfind_norecover'] = False
					self.edit_success, self.edit_error = obj.move_item(dest)
					if self.edit_success:
						self.edit_redirect_to = obj.get_absolute_url()
				else:
					self.edit_success = False
					self.edit_error = 'quickedit_cat_invalid_id'
			
			else:
				self.edit_cmd_handled = False
	
	def get_queryset(self, *args, **kwargs):
		return super(category_list, self).get_queryset(*args, **kwargs).select_related('background_tag', 'access_code')
	
	# We have an object and can view it
	def get_context_canview(self, context, **kwargs):
		context = super(category_list, self).get_context_canview(context, **kwargs)
		if self.g2redir and context['object'].get_absolute_url() != self.g2redir:
			self.request.session['deerfind_path'] = self.g2redir
			raise Http404
		
		if context['can_edit']:
			context['edit_mode'] = 'cat'
		
		has_blocks, blocks = self.assemble_blocks(context['object'], 'category', context['object'].view_type)
		if has_blocks:
			context['rss_feed'] = True
			context.update(blocks)
		else:
			context['rss_feed'] = False
			context['error'] = 'cat_empty'
		
		# Breadcrumbs
		ancestors = context['object'].get_ancestors(include_self=True)
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		for crumb in ancestors:
			context['breadcrumbs'].append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
		
		context['title_page'] = str(context['object'])
		context['highlight_featured'] = self.highlight_featured
		context['body_text'] = sunset_embed(context['object'].body_html, self.request)
		
		if context['object'].summary_short:
			context['sitemeta_desc'] = context['object'].summary_short
		else:
			context['sitemeta_desc'] = "Directory:  %s" % (str(context['object']))
		
		return context


class tag_list(leaf_parent, DetailView):
	model = tag
	
	def dispatch(self, *args, **kwargs):
		# Stupid corner cases where stupid AI bots love to throw wrong query arguments at every URL
		if 'mode=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?mode=)')
		elif 'display=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?display=)')
		elif 'reply_to=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?reply_to=)')
		
		return super(tag_list,self).dispatch(*args, **kwargs)
	
	def get_queryset(self, *args, **kwargs):
		return super(tag_list, self).get_queryset(*args, **kwargs).prefetch_related('synonyms')
	
	def get_context_data(self, **kwargs):
		context = super(tag_list,self).get_context_data(**kwargs)
		canview, view_restriction = context['object'].can_view(self.request)
		if not canview:
			if view_restriction == 'access_404':
				self.request.session['deerfind_norecover'] = True
				raise Http404
			else:
				context['object'] = ''
				context['error'] = view_restriction
		
		else:
			context['highlight_featured'] = self.highlight_featured
			context['no_access_codes'] = True
			context['synonym_list'] = context['object'].synonyms.all()
			if context['object'].can_edit(self.request)[0]:
				context['return_to'] = context['object'].get_absolute_url()
				context['can_edit'] = True
				context['edit_mode'] = 'tags'
			
			blocks = self.assemble_blocks(context['object'],'tag',context['object'].view_type)
			if blocks[0]:
				context.update(blocks[1])
				context['rss_feed'] = True
			else:
				context['error'] = 'tag_empty'
			
			if not context.get('breadcrumbs',False):
				context['breadcrumbs'] = []
			
			context['breadcrumbs'].append({'url':reverse('all_tags'), 'title':'Tags'})
			context['breadcrumbs'].append({'url':reverse('tag',kwargs={'slug':context['object'].slug,}), 'title':unicode(context['object'])}) # type: ignore
			
			context['body_text'] = sunset_embed(context['object'].body_html, self.request)
			
			context['title_page'] = str(context['object'])
			if context['object'].summary_short:
				context['sitemeta_desc'] = context['object'].summary_short
			else:
				context['sitemeta_desc'] = "Tag:  %s" % (str(context['object']))
		
		return context


# RSS Feeds
class main_rssfeed(leaf_parent, Feed):
	title_text = "Lupinia Studios"
	author_name = "Natasha L."
	item_author_name = "Natasha L."
	description = "Photography, writing, and creative works by Natasha L."
	feed_copyright = timezone.now().strftime('Copyright (c) 2000-%Y Natasha L.')
	parent_type = 'main_feed'
	
	def title(self, obj=None):
		if obj:
			return '%s - %s' % (self.title_text, unicode(obj)) # type: ignore
		else:
			return self.title_text
	
	def link(self, obj=None):
		if obj:
			return obj.get_absolute_url()
		else:
			return "/"
	
	def items(self, obj=None):
		if obj:
			return self.get_leaves(parent=obj, parent_type = self.parent_type, is_feed=True)[:100]
		else:
			return self.get_leaves(parent_type = 'main_feed', is_feed=True)[:100]
	
	def item_title(self, item):
		leaf_item = getattr(item, item.type, None)
		return u'%s - %s' % (item.type.capitalize(), unicode(leaf_item)) # type: ignore
	
	def item_link(self, item):
		leaf_item = getattr(item, item.type, None)
		url_func = getattr(leaf_item, 'get_absolute_url', None)
		if url_func:
			return url_func()
		else:
			return None
	
	def item_pubdate(self, item):
		return item.timestamp_post
	
	def item_updateddate(self, item):
		return item.timestamp_mod
	
	def item_categories(self, item):
		return item.tags.all().values_list('slug', flat=True)
	
	def item_description(self, item):
		leaf_item = getattr(item, item.type, None)
		return getattr(leaf_item, 'rss_description', 'No Description')
	
	def item_enclosure_url(self, item):
		leaf_item = getattr(item, item.type, None)
		enclosure_obj = getattr(leaf_item, 'rss_enclosure_obj', None)
		return getattr(enclosure_obj, 'rss_enclosure_url', None)
	
	def item_enclosure_length(self, item):
		leaf_item = getattr(item, item.type, None)
		enclosure_obj = getattr(leaf_item, 'rss_enclosure_obj', None)
		return getattr(enclosure_obj, 'rss_enclosure_length', None)
	
	def item_enclosure_mime_type(self, item):
		leaf_item = getattr(item, item.type, None)
		enclosure_obj = getattr(leaf_item, 'rss_enclosure_obj', None)
		return getattr(enclosure_obj, 'rss_enclosure_type', None)


class cat_rssfeed(main_rssfeed):
	parent_type = 'category'
	
	def get_object(self, request, cached_url):
		obj = get_object_or_404(category, cached_url=cached_url)
		if obj.can_view(request)[0]:
			return obj
		else:
			request.session['deerfind_norecover'] = True
			raise Http404


class tag_rssfeed(main_rssfeed):
	parent_type = 'tag'
	
	def get_object(self, request, slug):
		obj = get_object_or_404(tag, slug=slug)
		if obj.can_view(request)[0]:
			return obj
		else:
			request.session['deerfind_norecover'] = True
			raise Http404


#	Helper functions imported by other views
def finder(request):
	"""
	Standard 404 recovery function for all DeerTrees objects.
	Requires a request to process.
	If request.path starts with /tags/, will check for tag or tag_synonym
	Else, second check is for special_feature objects.
	Else, third check is for category objects.
	
	Must return a tuple:
		is_found:  Boolean, indicates whether a match was returned
		found_url:  String, contains the URL to redirect to
	"""
	is_found = False
	found_url = ''
	
	check_tags = False
	check_special_features = True
	check_cats = True
	
	path = urlpath(request.path, force_lower=True)
	reverse_suffix = ''
	is_index_file = False
	
	# STEP 1:  Figure out what we're going to do
	if path.root_dir == 'tags':
		# Only potentially check for tags if we're in the tags folder
		check_tags = True
		check_cats = False
		check_special_features = False
	
	if path.is_file:
		# Only certain types of files can be found by this function
		if path.filetype in ['rss', 'atom', 'xml']:
			# This appears to be an RSS feed
			suffix_matches = {
				'feed':'_rss',
				'featured-images':'_rss_images_featured',
				'recent-images':'_rss_images_recent',
			}
			reverse_suffix = suffix_matches.get(path.filename, '')
			if not reverse_suffix:
				# Undefined RSS feed
				check_cats = False
				check_tags = False
			else:
				# We have a match!
				if check_tags and path.cwd == 'tags':
					# Corner case:  We're in the tags root directory, so this is invalid
					is_found = True
				
				if path.filetype != 'xml':
					# Special case:  XML might be a special feature
					check_special_features = False
		
		elif path.filetype == 'cfm':
			# Special system/aggregate views
			suffix_matches = {
				'featured-images':'_images_featured',
				'recent-images':'_images_recent',
			}
			reverse_suffix = suffix_matches.get(path.filename, '')
			if reverse_suffix:
				# We have a match!
				check_special_features = False
				if check_tags and path.cwd == 'tags':
					# Corner case:  We're in the tags root directory, so this is invalid
					is_found = True
			else:
				# Undefined aggregate/special view
				check_cats = False
				check_tags = False
		
		elif path.filename == 'index' or path.filename == 'default':
			# Someone sniffing around trying to find index files, but I'll allow it
			is_index_file = True
			if check_tags and path.cwd == 'tags':
				# Corner case:  We're in the tags root directory
				is_found = True
				found_url = reverse('all_tags')
			elif not path.root_dir:
				# Corner case:  This is the root of the site!
				is_found = True
				found_url = '/'
		
		else:
			# Request is for a file, but this is the view where we mostly look for directories
			check_cats = False
			check_tags = False
	
	# STEP 2:  Check tags!
	if check_tags and not is_found:
		# Guess we're doin' tags now
		# First check:  Matching a tag takes priority
		# It would be more efficient to do this all in one query,
		# but there's potential for duplication between tags and synonyms.
		# In this situation, the tag must take precedence,
		# but I'm not sure how to sort a queryset like that.
		tag_check = tag.objects.filter(slug__iexact=path.cwd).first()
		if not tag_check:
			# Second check: If this isn't a tag, maybe it's a synonym
			tag_check = tag.objects.filter(synonyms__slug__iexact=path.cwd).first()
		
		# Did we get something?
		if tag_check:
			# Found it!  Yay!
			is_found = True
			perm_check, reason = tag_check.can_view(request)
			if perm_check:
				found_url = reverse('tag%s' % reverse_suffix, kwargs={'slug':tag_check.slug,})
		else:
			# We found nothing, but /tags is a special directory, so nothing else should be checked
			is_found = True
			found_url = ''
	
	# STEP 3:  Check special features!
	if check_special_features and not is_found:
		if is_index_file:
			# Corner case: Someone tried to look for an index file in a special_feature that behaves like a directory
			feature_check = special_feature.objects.filter(url__iexact=path.cwd, directory=True).select_related().first()
		else:
			feature_check = special_feature.objects.filter(url__iexact=path.basename).select_related().first()
		
		if feature_check and feature_check.url_reverse:
			is_found = True
			perm_check, reason = feature_check.can_view(request)
			if perm_check:
				found_url = reverse(feature_check.url_reverse)
			else:
				# We found something, but without permission to view it, so stop looking
				found_url = ''
	
	# STEP 4:  Check categories!
	# TO DO:  This logic is wrong and needs to be rewritten
	if check_cats and not is_found:
		search_slug = path.basename
		if path.is_file:
			search_slug = path.cwd
		
		cat_check = category.objects.filter(slug__iexact=search_slug).select_related().first()
		if cat_check:
			is_found = True
			perm_check, reason = cat_check.can_view(request)
			if perm_check:
				found_url = reverse('category',kwargs={'cached_url':cat_check.cached_url,})
			else:
				# We found something, but without permission to view it, so stop looking
				found_url = ''
	
	# STEP 5: All done!  Return whatever we found, if we found anything!
	return (is_found, found_url)


def subcats(parent=False, parent_type=False, request=False):
	if parent_type == 'category' and parent:
		child_cats = parent.children.filter(access_query(request)).order_by('-featured','title').select_related('icon')
		
		if child_cats:
			return child_cats
		else:
			return False
	else:
		return False


class leaf_view(access_view):
	slug_field = 'basename'
	slug_url_kwarg = 'slug'
	
	def edit_object(self, obj):
		super(leaf_view, self).edit_object(obj)
		
		if not self.edit_cmd_handled:
			self.edit_cmd_handled = True
			
			# Pull known arguments
			cmd = self.request.GET.get('alitelvdi', '')
			target = self.request.GET.get('diyosdi', None)
			
			if cmd == 'mv':
				# Move to a different parent directory (category)
				# Requires diyosdi (target) parameter
				if target and is_int(target):
					self.request.session['deerfind_norecover'] = True
					dest = get_object_or_404(category, pk=int(target))
					self.request.session['deerfind_norecover'] = False
					self.edit_success, self.edit_error = obj.move_item(dest)
					if self.edit_success:
						self.edit_redirect_to = obj.get_absolute_url()
				else:
					self.edit_success = False
					self.edit_error = 'quickedit_cat_invalid_id'
			
			elif cmd == 'tag' or cmd == 'untag':
				# Add or remove tags
				# Requires diyosdi (target) parameter
				if target and is_int(target):
					self.request.session['deerfind_norecover'] = True
					target = get_object_or_404(tag, pk=int(target))
					self.request.session['deerfind_norecover'] = False
					if cmd == 'tag':
						obj.tags.add(target)
						self.edit_success = True
					elif cmd == 'untag':
						obj.tags.remove(target)
						self.edit_success = True
				else:
					self.edit_success = False
					self.edit_error = 'quickedit_tag_invalid_id'
			
				self.edit_success = False
				self.edit_success = False
			
			else:
				self.edit_cmd_handled = False
	
	def get_queryset(self, *args, **kwargs):
		return super(leaf_view, self).get_queryset(*args, **kwargs).filter(cat__cached_url=self.kwargs.get('cached_url', None)).select_related('access_code','cat').prefetch_related('tags')
	
	# We have an object and can view it
	def get_context_canview(self, context, **kwargs):
		context = super(leaf_view,self).get_context_canview(context, **kwargs)
		
		# Tags
		if self.request.user.is_superuser:
			context['tags'] = context['object'].tags.all()
		else:
			context['tags'] = context['object'].tags.filter(public=True)
		context['category'] = context['object'].cat
		
		# Breadcrumbs
		ancestors = context['object'].cat.get_ancestors(include_self=True)
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		for crumb in ancestors:
			context['breadcrumbs'].append({'url':reverse('category',kwargs={'cached_url':crumb.cached_url,}), 'title':crumb.title})
		
		context['breadcrumbs'].append({'url':context['object'].get_absolute_url(), 'title':str(context['object'])})
		
		# Metadata
		context['sitemeta_page_type'] = 'article'
		context['title_page'] = str(context['object'])
		context['permalink'] = context['object'].get_complete_url(self.request)
		context['sitemeta_category'] = str(context['object'].cat)
		context['sitemeta_timestamp_pub'] = context['object'].timestamp_post
		context['sitemeta_timestamp_mod'] = context['object'].timestamp_mod
		context['sitemeta_article_tags'] = context['object'].tags_list
		
		if not context['object'].admin_owned:
			context['sitemeta_article_author_name'] = context['object'].author
		
		# External links
		context['external_links'] = context['object'].get_links(self.request)
		# This really should be easier
		normal_link_count = context['external_links'].aggregate(c=Sum(Case(When(link_type__featured=False, then=1), output_field=IntegerField())))['c']
		if normal_link_count < 3:
			context['external_links_wide'] = True
		
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
class all_cats(TemplateView, special_feature_view):
	template_name = 'deertrees/sitemap.html'
	
	def dispatch(self, *args, **kwargs):
		# Stupid corner cases where stupid AI bots love to throw wrong query arguments at every URL
		if 'mode=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?mode=)')
		elif 'display=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?display=)')
		elif 'reply_to=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?reply_to=)')
		
		return super(all_cats,self).dispatch(*args, **kwargs)
	
	def get_context_data(self, **kwargs):
		context = super(all_cats,self).get_context_data(**kwargs)
		context['view'] = 'catlist'
		context['cats'] = category.objects.filter(access_query(self.request)).annotate(num_leaves=Count('leaves'))
		context['breadcrumbs'] = self.breadcrumbs()
		
		if self.request.GET.get('return_to', False) and self.request.GET.get('cmd', False) and self.request.user.has_perm('deertrees.change_leaf'):
			context['return_to'] = '%s?alitelvdi=%s&diyosdi=' % (self.request.GET.get('return_to', ''), self.request.GET.get('cmd', ''))
			context['title_page'] = "Select a Category"
		else:
			context['title_page'] = "All Categories"

		
		return context


class sitemap(all_cats):
	template_name = 'deertrees/sitemap.html'
	
	def get_context_data(self, **kwargs):
		context = super(sitemap,self).get_context_data(**kwargs)
		context['view'] = 'sitemap'
		context['cats'] = context['cats'].filter(sitemap_include=True)
		context['tags'] = tag.objects.filter(sitemap_include=True).annotate(num_leaves=Count('leaves'))
		if not self.request.user.is_superuser:
			context['tags'] = context['tags'].filter(public=True)
		context['title_page'] = "Site Map"
		return context


class all_tags(ListView):
	template_name = 'deertrees/taglist.html'
	model = tag
	context_object_name = 'tags'
	
	def dispatch(self, *args, **kwargs):
		# Stupid corner cases where stupid AI bots love to throw wrong query arguments at every URL
		if 'mode=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?mode=)')
		elif 'display=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?display=)')
		elif 'reply_to=' in self.request.META.get('QUERY_STRING',''):
			raise BadRequest('invalid query argument (?reply_to=)')
		
		return super(all_tags,self).dispatch(*args, **kwargs)
	
	def get_queryset(self, *args, **kwargs):
		query = super(all_tags, self).get_queryset(*args, **kwargs)
		
		if self.request.GET.get('return_to',False) and self.request.user.has_perm('deertrees.change_leaf'):
			pass
		else:
			query = query.filter(sitemap_include=True, leaves__isnull=False)
		
		if not self.request.user.is_superuser:
			query = query.filter(public=True)
		
		return query.annotate(num_leaves=Count('leaves')).order_by('-num_leaves','slug')
	
	def get_context_data(self, **kwargs):
		context = super(all_tags,self).get_context_data(**kwargs)
		context['no_access_codes'] = True
		
		if not context['tags']:
			context['error'] = 'no_tags'
		
		if not context.get('breadcrumbs',False):
			context['breadcrumbs'] = []
		
		context['breadcrumbs'].append({'url':reverse('all_tags'), 'title':'Tags'})
		
		if self.request.GET.get('return_to',False) and self.request.GET.get('cmd', False) and self.request.user.has_perm('deertrees.change_leaf'):
			context['return_to'] = '%s?alitelvdi=%s&diyosdi=' % (self.request.GET.get('return_to', ''), self.request.GET.get('cmd', ''))
			context['title_page'] = "Select a Tag"
		else:
			context['title_page'] = "All Tags"
		
		return context
