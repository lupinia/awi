#	DeerBooks (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Search Index Objects
#	=================

from django.utils import timezone

from haystack import indexes

from deerbooks.models import page

class page_index(indexes.SearchIndex, indexes.Indexable):
	# REQUIRED - Primary Content Fields
	title = indexes.CharField()	# SET BY METHOD
	summary = indexes.CharField(model_attr='summary_short', null=True)
	text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/deerbooks.txt')
	url = indexes.CharField(model_attr='get_absolute_url')
	
	# REQUIRED - Primary Facet/Filter Fields
	pub_date = indexes.DateTimeField(model_attr='timestamp', faceted=True)
	sites = indexes.MultiValueField()	# SET BY METHOD
	mature = indexes.BooleanField(model_attr='mature', faceted=True)
	security = indexes.IntegerField(model_attr='security')
	
	# Nullable Primary Fields/Facets
	parent = indexes.CharField(model_attr='cat', faceted=True)
	tags = indexes.MultiValueField(faceted=True)	# SET BY METHOD
	featured = indexes.BooleanField(model_attr='featured', faceted=True)
	
	
	# Standard methods
	def get_updated_field(self):
		return 'timestamp_mod'
	
	def get_model(self):
		return page
	
	def index_queryset(self, using=None):
		return self.get_model().objects.filter(published=True, timestamp_post__lte=timezone.now()).select_related().prefetch_related('sites')
	
	def prepare(self, obj):
		data = super(page_index, self).prepare(obj)	# ALWAYS DIFFERENT
		data['_boost'] = 1.5
		return data
	
	
	# Per-field methods
	def prepare_title(self, obj):
		return unicode(obj) # type: ignore
	
	def prepare_sites(self, obj):
		return [site.pk for site in obj.sites.all()]
	
	def prepare_tags(self, obj):
		return [tag.display_title for tag in obj.tags.all()]
