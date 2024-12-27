#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Utility functions/objects for string/text operations
#	=================

from django.utils.html import linebreaks, strip_tags

#	Convert text that may or may not contain HTML formatting to proper HTML paragraphs/line breaks.
def format_html(input_string):
	if not input_string:
		return input_string
	if "<p>" in input_string or "<br />" in input_string:
		return input_string
	else:
		return linebreaks(input_string)

#	Shorten the input_string to the specified length.
def truncate(input_string, length=255):
	if not input_string or not length:
		# No input, so do nothing.
		return None
	
	if len(input_string) <= length:
		# Already the right length
		return input_string
	else:
		# Trim input_string to length, then split off any interrupted words, then add an ellipsis.
		return input_string[:length].rsplit(' ',1)[0]+'...'

#	Generate a short summary for any longer strings.
#	This was a model method originally, but putting it here is less repetitive.
#	Plus, this can be more powerful and useful than what I could justify with model methods.
#	Parameters:
#		length:  Target maximum character length of summary.  Default: 255 (same as a CharField)
#		body:  The primary body text for the model.  Usually a TextField with unlimited length.
#		summary:  An existing short-summary CharField (<= 255 characters).  If given, this is used in place of body unless length parameter > 255.
#		fallback:  What to return if body and summary are both empty.  Example use-case:  When body and summary are both optional on a model, but it's vital to get a summary of some sort anyway, return the title.
#		strip:  If False, strip_tags will not be run.  Not recommended, but could be necessary in some cases.
#		prefer_long:  If True, summary will only be used if its len >= length.  Useful when you know you want a string of a certain length but your summary value might be far shorter than that, despite the summary value being non-empty.
def summarize(body=None, length=255, summary=None, fallback=None, strip=True, prefer_long=False):
	if not body and not summary:
		# Nothing to do!
		return fallback
	
	result = None
	
	# If there's a summary, we'll try that first.
	# if prefer_long == False, summary is the priority
	# if prefer_long == True and len(summary) >= length, summary is still the priority
	if summary and (not prefer_long or (prefer_long and len(summary) >= length)):
		summary = strip_tags(summary)
		result = truncate(summary, length)
	
	# If we don't have anything at this point, for whatever reason, we'll try the body text.
	if result is None and body:
		body = strip_tags(body)
		result = truncate(body, length)
	
	if not result:
		# After all that, we still don't have anything.
		return fallback
	else:
		# We did the thing!  Whether it was the right thing is up to you, but this part worked correctly!
		return result
