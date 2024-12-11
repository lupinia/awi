#	Awi Error (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class error(models.Model):
	SEVERITY_OPTIONS=(
		('critical','Critical (Red)'),
		('warning','Warning (Orange)'),
		('notice','Notice (Blue)')
	)
	
	error_key = models.SlugField(unique=True, help_text='The machine name for this error, used by code to reference it.')
	severity = models.CharField(max_length=12, choices=SEVERITY_OPTIONS, default='critical')
	message = models.TextField()
	js_error = models.BooleanField(blank=True, verbose_name='Javascript error?', help_text='Check this box if this error should only be displayed if Javascript is disabled (uses a noscript tag instead of a div).')
	
	def __str__(self):
		return self.error_key
	
	@property
	def element(self):
		if self.js_error:
			return 'noscript'
		else:
			return 'div'
	
	class Meta:
		verbose_name = 'error message'
