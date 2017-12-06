#	DeerFood (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Search Index Objects
#	=================

from django.contrib.sites.models import Site
from django.utils import timezone

from haystack import indexes

from deerfood.models import menu_item

class food_index(indexes.SearchIndex, indexes.Indexable):
	# REQUIRED - Primary Content Fields
	title = indexes.CharField(model_attr='name')
	summary = indexes.CharField(model_attr='summary_short', null=True)
	text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/deerfood.txt')
	url = indexes.CharField()	# SET BY METHOD
	
	# REQUIRED - Primary Facet/Filter Fields
	pub_date = indexes.DateTimeField(model_attr='timestamp_mod', faceted=True)
	sites = indexes.MultiValueField(default=list(Site.objects.all().values_list('pk', flat=True)))
	mature = indexes.BooleanField(default=False, faceted=True)
	security = indexes.IntegerField(default=0)
	
	# Nullable Primary Fields/Facets
	parent = indexes.CharField(model_attr='section', null=True, faceted=True)
	tags = indexes.MultiValueField(faceted=True)	# SET BY METHOD
	
	
	# Standard methods
	def get_updated_field(self):
		return 'timestamp_mod'
	
	def get_model(self):
		return menu_item
	
	def index_queryset(self, using=None):
		return self.get_model().objects.filter(timestamp_post__lte=timezone.now()).select_related().prefetch_related('flags')
	
	def prepare(self, obj):
		data = super(food_index, self).prepare(obj)	# ALWAYS DIFFERENT
		data['_boost'] = 0.9
		return data
	
	
	# Per-field methods
	def prepare_url(self, obj):
		return obj.section.get_absolute_url()
	
	def prepare_tags(self, obj):
		return [flag.name for flag in obj.flags.all()]
