#	Awi Background (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Template Tags
#	bg_filename:	Returns a url to a background image fitting the given tags
#	bg_info:		Returns text giving a title and info link for the current background
#	
#	TODO:	Session storage, to reduce data transfer
#	=================

from django import template
from django.db.models import Q
register = template.Library()

from awi_bg.models import background

cur_background = False

def bg_filename(input_string=''):
	global cur_background
	bg_array=background.objects.filter(Q(tags__tag=input_string) | Q(tags__tag='main'))
	
	import random
	bg_selected=random.choice(bg_array)
	cur_background = bg_selected
	return bg_selected.filename

def bg_info(input_string=''):
	global cur_background
	bg_selected=cur_background
	return 'Background Photo:  <a href="'+bg_selected.gallery_id+'">'+bg_selected.title+'</a>'
	
register.simple_tag(bg_filename)
register.simple_tag(bg_info)
