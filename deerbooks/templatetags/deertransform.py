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

import re
import markdown
import html2text
from django import template

def html_md(input_string, promote=True):
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
	
	return md

def html_txt(input_string, promote=True):
	md = html_md(input_string, promote)
	txt = md.replace('* * *','---')
	txt = txt.replace(' * ',' - ')
	txt = re.sub(r'\*\*(.*)\*\*',r'*\1*',txt)
	txt = re.sub(r'!\[.*?\]\((.*?)\)',r'(Image:  \1)',txt)
	txt = re.sub(r'([0-9]+)\\\.',r'\1.',txt)
	
	return txt

def html_tex(input_string, promote=True):
	md = html_md(input_string, promote)
	md = re.sub(r'\((/.*?)\)',r'(http://www.lupinia.net\1)',md)	
	md = re.sub(r'!\[.*?\]\((.*?)\)',r'(Image:  \1)',md)
	
	mdparse = markdown.Markdown(None,extensions=['latex'])
	tex = mdparse.convert(md)
	tex = tex.replace('<root>','')
	tex = tex.replace('</root>','')
	tex = tex.replace(r'$',r'{\$}')
	tex = tex.replace(r'_',r'{\_}')
	tex = tex.replace(r'&',r'{\&}')
	tex = re.sub(r'([0-9]+)\\\.',r'\1.',tex)
	
	return tex

register = template.Library()

register.simple_tag(html_md)
register.simple_tag(html_txt)
register.simple_tag(html_tex)