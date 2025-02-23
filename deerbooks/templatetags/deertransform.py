#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Template Tags
#	html_md:		Converts from HTML to Markdown
#	html_txt:		Converts from HTML to plain text (unicode)
#	html_tex:		Converts from HTML to LaTeX
#	=================

import html2text
import markdown
import re

from django import template
from django.utils.safestring import mark_safe

def html_md(input_string, promote=True):
	"""
	Django template tag for converting HTML to Markdown.
	Returns a string that has already been marked "safe" due to special formatting.
	Sanitize before calling this!
	
	Parameters:
		input_string (str): The HTML content to be converted
		promote (bool): Optional, increments headers if True (H3 -> H2, etc)
	"""
	md_maker = html2text.HTML2Text()
	md_maker.unicode_snob = True
	md_maker.bypass_tables = False
	md_maker.skip_internal_links = True
	md_maker.body_width = 0
	
	md = md_maker.handle(input_string)
	md = re.sub(r'\((/.*?)\)',r'(http://www.lupinia.net\1)',md)
	
	if promote:
		# Making an assumption here that I'll never use a header greater than H3 in a Page object
		md = re.sub('(### )','## ',md)
		md = re.sub('(#### )','### ',md)
		md = re.sub('(##### )','#### ',md)
		md = re.sub('(###### )','##### ',md)
	
	return mark_safe(md)

def html_txt(input_string, promote=True):
	"""
	Template tag for converting HTML to plain text
	Returns a string that has already been marked "safe" due to special formatting.
	Sanitize before calling this!
	
	Parameters:
		input_string (str): The HTML content to be converted
		promote (bool): Optional, increments headers if True (H3 -> H2, etc)
	"""
	md = html_md(input_string, promote)
	txt = md.replace('* * *','---')
	txt = txt.replace(' * ',' - ')
	txt = re.sub(r'\*\*(.*)\*\*',r'*\1*',txt)
	txt = re.sub(r'!\[.*?\]\((.*?)\)',r'(Image:  \1)',txt)
	txt = re.sub(r'([0-9]+)\\\.',r'\1.',txt)
	
	return mark_safe(txt)

def html_tex(input_string, promote=True):
	"""
	Template tag for converting HTML to LaTeX
	Returns a string that has already been marked "safe" due to special formatting.
	Sanitize before calling this!
	
	Parameters:
		input_string (str): The HTML content to be converted
		promote (bool): Optional, increments headers if True (H3 -> H2, etc)
	"""
	md = html_md(input_string, promote)
	md = re.sub(r'\((/.*?)\)',r'(http://www.lupinia.net\1)',md)	
	md = re.sub(r'!\[.*?\]\((.*?)\)',r'(Image:  \1)',md)
	
	mdparse = markdown.Markdown(None,extensions=['latex'])
	tex = mdparse.convert(md)
	tex = tex.replace('<root>','')
	tex = tex.replace('</root>','')
	tex = tex.replace('\\(','(')
	tex = tex.replace('\\)',')')
	tex = tex.replace('_','\\_')
	tex = tex.replace('&','\\&')
	tex = re.sub(r'([0-9]+)\\\.',r'\1.',tex)
	
	return mark_safe(tex)

def field_tex(input_string):
	"""
	Template tag for converting a single string to LaTeX
	Returns a string that has already been marked "safe" due to special formatting.
	Sanitize before calling this!
	
	Parameters:
		input_string (str): The HTML content to be converted
	"""
	tex = input_string.replace('_','\\_')
	tex = tex.replace('#','\\#')
	tex = tex.replace('$','\\$')
	tex = tex.replace('&','\\&')
	
	return mark_safe(tex)

register = template.Library()

register.simple_tag(html_md)
register.simple_tag(html_txt)
register.simple_tag(html_tex)
register.simple_tag(field_tex)