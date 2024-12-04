#	DeerTrees (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Search Index Objects
#	=================

from django.contrib.sites.models import Site
from django.utils import timezone

from haystack import indexes

from deertrees.models import category, tag

class category_index(indexes.SearchIndex, indexes.Indexable):
	# REQUIRED - Primary Content Fields
	title = indexes.CharField()	# SET BY METHOD
	summary = indexes.CharField(model_attr='summary_short', null=True)
	text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/deertrees.txt')
	url = indexes.CharField(model_attr='get_absolute_url')
	
	# REQUIRED - Primary Facet/Filter Fields
	pub_date = indexes.DateTimeField(model_attr='timestamp_mod', faceted=True)
	sites = indexes.MultiValueField()	# SET BY METHOD
	mature = indexes.BooleanField(model_attr='mature', faceted=True)
	security = indexes.IntegerField(model_attr='security')
	
	# Nullable Primary Fields/Facets
	parent = indexes.CharField(model_attr='parent', null=True, faceted=True)
	featured = indexes.BooleanField(model_attr='featured', faceted=True)
	
	# Optional Display Fields
	thumb = indexes.CharField(model_attr='icon_url', indexed=False, null=True)
	item_count = indexes.IntegerField(indexed=False, null=True)	# SET BY METHOD
	
	
	# Standard methods
	def get_updated_field(self):
		return 'timestamp_mod'
	
	def get_model(self):
		return category
	
	def index_queryset(self, using=None):
		return self.get_model().objects.filter(published=True, trash=False, timestamp_post__lte=timezone.now())
	
	def prepare(self, obj):
		data = super(category_index, self).prepare(obj)	# ALWAYS DIFFERENT
		data['_boost'] = 1.1
		return data
	
	
	# Per-field methods
	def prepare_title(self, obj):
		return unicode(obj) # type: ignore
	
	def prepare_sites(self, obj):
		return [site.pk for site in obj.sites.all()]
	
	def prepare_item_count(self, obj):
		return obj.leaves.all().count()


class tag_index(indexes.SearchIndex, indexes.Indexable):
	# REQUIRED - Primary Content Fields
	title = indexes.CharField(model_attr='display_title')
	summary = indexes.CharField(model_attr='summary_short', null=True)
	text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/deertrees.txt')
	url = indexes.CharField(model_attr='get_absolute_url')
	
	# REQUIRED - Primary Facet/Filter Fields
	pub_date = indexes.DateTimeField(model_attr='timestamp_mod', faceted=True)
	sites = indexes.MultiValueField(default=list(Site.objects.all().values_list('pk', flat=True)))
	mature = indexes.BooleanField(default=False, faceted=True)
	security = indexes.IntegerField(default=0)
	
	# Nullable Primary Fields/Facets
	#	None present for this model
	
	# Optional Display Fields
	item_count = indexes.IntegerField(indexed=False, null=True)	# SET BY METHOD
	
	
	# Standard methods
	def get_updated_field(self):
		return 'timestamp_mod'
	
	def get_model(self):
		return tag
	
	def index_queryset(self, using=None):
		return self.get_model().objects.filter(sitemap_include=True, timestamp_post__lte=timezone.now())
	
	def prepare(self, obj):
		data = super(tag_index, self).prepare(obj)	# ALWAYS DIFFERENT
		data['_boost'] = 0.5
		return data
	
	
	# Per-field methods
	def prepare_item_count(self, obj):
		return obj.leaves.all().count()
