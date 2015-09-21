#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.views import generic
from django.utils import timezone
from collections import OrderedDict
from itertools import cycle

from deertrees.models import category, tag, leaf

class leaf_parent():
	template_name = 'deertrees/leaves.html'
	homepage = False
	
	def get_leaves(self, parent=False, parent_type=False):
		leaf_filters = {}
		
		leaf_ordering = ['-featured','-timestamp_post']
		leaf_filters['timestamp_post__lte'] = timezone.now()
		
		if self.homepage == True:
			leaf_ordering = ['-timestamp_post',]
			leaf_filters['featured'] = True
		elif parent_type == 'main_feed':
			leaf_ordering = ['-timestamp_post',]
		elif parent_type == 'category' and parent:
			leaf_filters['cat'] = parent
		elif parent_type == 'tag' and parent:
			leaf_filters['tags'] = parent
		
		from awi_access.models import access_query
		leaves = leaf.objects.filter(**leaf_filters).filter(access_query(self.request)).order_by(*leaf_ordering).select_related()
		
		if leaves:
			return leaves
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
		
		from django.conf import settings
		blocks_map = settings.DEERTREES_BLOCKS
		blocks = {}
		blocks_count = {}
		assigned_to_blocks = []
		returned_data = [False,{}]
		
		#	Build the list of blocks to assign
		blockname_cycle = cycle(['sidebar','main_half'])
		blocks_to_assign = ['sidebar','sidebar','main_full_2']
		if parent and parent.content_priority is not 'desc':
			blocks_to_assign.insert(0,'main_full_1')
		
		#	Loop the known-existing content types, to get a list.  We'll deal with priority later.
		for type, settings_dict in blocks_map.iteritems():
			blocks[type] = []
			blocks_count[type] = 0
		
		#	Content time!
		#	First, check for subcategories
		if parent_type == 'category' and parent:
			child_cats = parent.children.all().order_by('title')
			if child_cats:
				blocks['category'] = child_cats
		
		#	Now get items in this category
		leaves = self.get_leaves(parent,parent_type)
		if leaves:
			#	1.  Loop all of our leaves
			#	2.  For each leaf, loop blocks_map to find its type
			#	3.  Once that check is successful, put it in the correct block dictionary
			for leaf_item in leaves:
				for type, settings in blocks_map.iteritems():
					leaf_assigned = False
					if blocks_count[type] <= 12:
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
				returned_data[1]['main_full_1'] = {'type':parent.content_priority,'data':blocks[parent.content_priority],'template':blocks_map[parent.content_priority]['template'] % {'type':'main',}}
				blocks_to_assign.pop(0)
				blocks.pop(parent.content_priority)
			
			#	Make sure we didn't just pop off the last/only one.
			if blocks:
				order_main = {}
				order_sidebar = {}
				blockorder_main_iter = False
				blockorder_sidebar_iter = False
				
				#	Now, let's build a priority list per region
				for type, content in blocks.iteritems():
					if blocks_map[type].get('sidebar',False):
						order_sidebar[str(blocks_map[type]['sidebar'])] = {'type':type,'data':content,'template':blocks_map[type]['template'] % {'type':'sidebar',}}
					if blocks_map[type].get('main',False):
						order_main[str(blocks_map[type]['main'])] = {'type':type,'data':content,'template':blocks_map[type]['template'] % {'type':'main',}}
				
				#	And now put them in order
				if order_main:
					blockorder_main = OrderedDict(sorted(order_main.items(), key=lambda t: t[0]))
					blockorder_main_iter = blockorder_main.itervalues()
				if order_sidebar:
					blockorder_sidebar = OrderedDict(sorted(order_sidebar.items(), key=lambda t: t[0]))
					blockorder_sidebar_iter = blockorder_sidebar.itervalues()
				
				#	Assign the main blocks first 
				for blockname in blocks_to_assign:
					if 'main' in blockname and blockorder_main_iter:
						blockdata = next(blockorder_main_iter,False)
						if blockdata and blockdata['type'] not in assigned_to_blocks:
							returned_data[1][blockname] = blockdata
							assigned_to_blocks.append(blockdata['type'])
					elif 'sidebar' in blockname and blockorder_sidebar_iter:
						blockdata = next(blockorder_sidebar_iter,False)
						if blockdata and blockdata['type'] not in assigned_to_blocks:
							if not returned_data[1].get('sidebar',False):
								returned_data[1]['sidebar'] = []
							returned_data[1]['sidebar'].append(blockdata)
							assigned_to_blocks.append(blockdata['type'])
				
				#	Quick bit of cleanup
				for content_type in assigned_to_blocks:
					blocks.pop(content_type,None)
				
				#	Is there anything left?
				if blocks:
					#	Seriously?  Ok then, we'll just go through whatever's left.
					#	Sidebar takes priority.
					for sidebar_data in blockorder_sidebar.values():
						if sidebar_data['type'] not in assigned_to_blocks:
							returned_data[1]['sidebar'].append(sidebar_data)
							assigned_to_blocks.append(sidebar_data['type'])
					
					for main_data in blockorder_main.values():
						if main_data['type'] not in assigned_to_blocks:
							if not returned_data[1]['main_half']:
								returned_data[1]['main_half'] = []
							returned_data[1]['main_half'].append(main_data)
							assigned_to_blocks.append(main_data['type'])
		
		return returned_data


class homepage(leaf_parent, generic.TemplateView):
	template_name='deertrees/home.html'
	homepage = True
	
	def get_context_data(self, **kwargs):
		context = super(homepage,self).get_context_data(**kwargs)
		
		blocks = self.assemble_blocks(parent_type = 'homepage')
		if blocks[0]:
			context.update(blocks[1])
		
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
		
		return context

class main_rssfeed(leaf_parent, generic.TemplateView):
	template_name='deertrees/rss.xml'
	
	def get_context_data(self, **kwargs):
		context = super(homepage,self).get_context_data(**kwargs)
		
		leaves = self.get_leaves(parent_type = 'homepage')
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
		
		return context

class tag_list(leaf_parent, generic.DetailView):
	model=tag
	
	def get_context_data(self, **kwargs):
		context = super(tag_list,self).get_context_data(**kwargs)
		
		blocks = self.assemble_blocks(context['object'],'tag')
		if blocks[0]:
			context.update(blocks[1])
		else:
			context['error'] = 'tag_empty'
		
		return context
