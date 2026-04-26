#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Template Tags
#	=================

from django import template

register = template.Library()

# This is so stupid, this should just be part of the standard library
# Why are you like this, Django?
def get_item(parent, key):
	return parent.get(key, None)

register.filter(get_item)
