#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Search Index Objects
#	=================

from django.utils import timezone

from haystack import indexes

from sunset.models import image

class image_index(indexes.SearchIndex, indexes.Indexable):
	# REQUIRED - Primary Content Fields
	title = indexes.CharField()	# SET BY METHOD
	summary = indexes.CharField(model_attr='summary_short', null=True)
	text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/sunset.txt')
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
	
	# Optional Display Fields
	thumb = indexes.CharField(indexed=False, null=True)	# SET BY METHOD
	
	
	# Standard methods
	def get_updated_field(self):
		return 'timestamp_mod'
	
	def get_model(self):
		return image
	
	def index_queryset(self, using=None):
		return self.get_model().objects.filter(published=True, is_new=False, timestamp_post__lte=timezone.now()).select_related().prefetch_related('assets', 'sites')
	
	def prepare(self, obj):
		data = super(image_index, self).prepare(obj)	# ALWAYS DIFFERENT
		data['_boost'] = 0.8
		return data
	
	
	# Per-field methods
	def prepare_title(self, obj):
		return unicode(obj) # type: ignore
	
	def prepare_sites(self, obj):
		return [site.pk for site in obj.sites.all()]
	
	def prepare_tags(self, obj):
		return [tag.display_title for tag in obj.tags.all()]
	
	def prepare_thumb(self, obj):
		thumb = obj.assets.filter(type='icon').first()
		if thumb:
			return thumb.get_url()
		else:
			return None
