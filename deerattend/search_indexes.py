#	DeerAttend (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Search Index Objects
#	=================

from django.contrib.sites.models import Site
from django.utils import timezone

from haystack import indexes

from deerattend.models import venue, event_instance

class event_index(indexes.SearchIndex, indexes.Indexable):
	# REQUIRED - Primary Content Fields
	title = indexes.CharField(model_attr='get_name',)
	summary = indexes.CharField(model_attr='summary_search', null=True)
	text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/deerattend_event.txt')
	url = indexes.CharField()	# SET BY METHOD
	
	# REQUIRED - Primary Facet/Filter Fields
	pub_date = indexes.DateTimeField(model_attr='date_start', faceted=True)
	sites = indexes.MultiValueField(default=list(Site.objects.all().values_list('pk', flat=True)))
	mature = indexes.BooleanField(model_attr='event__mature', faceted=True)
	security = indexes.IntegerField(default=0)
	
	# Nullable Primary Fields/Facets
	parent = indexes.CharField(model_attr='event__type', null=True, faceted=True)
	tags = indexes.MultiValueField(faceted=True)	# SET BY METHOD
	featured = indexes.BooleanField(model_attr='is_upcoming', faceted=True)
	
	
	# Standard methods
	def get_updated_field(self):
		return 'timestamp_mod'
	
	def get_model(self):
		return event_instance
	
	def index_queryset(self, using=None):
		return self.get_model().objects.filter(timestamp_post__lte=timezone.now()).select_related().prefetch_related('flags')
	
	def prepare(self, obj):
		data = super(event_index, self).prepare(obj)	# ALWAYS DIFFERENT
		data['_boost'] = 0.8
		return data
	
	
	# Per-field methods
	def prepare_url(self, obj):
		return obj.event.get_absolute_url()
	
	def prepare_tags(self, obj):
		return [flag.name for flag in obj.flags.all()]


class venue_index(indexes.SearchIndex, indexes.Indexable):
	# REQUIRED - Primary Content Fields
	title = indexes.CharField()	# SET BY METHOD
	text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/deerattend_venue.txt')
	url = indexes.CharField(model_attr='get_absolute_url')
	
	# REQUIRED - Primary Facet/Filter Fields
	pub_date = indexes.DateTimeField(model_attr='timestamp_mod', faceted=True)
	sites = indexes.MultiValueField(default=list(Site.objects.all().values_list('pk', flat=True)))
	mature = indexes.BooleanField(model_attr='events__event__mature', faceted=True)
	security = indexes.IntegerField(default=0)
	
	# Nullable Primary Fields/Facets
	#	None present for this model
	
	# Optional Display Fields
	item_count = indexes.IntegerField(indexed=False, null=True)	# SET BY METHOD
	
	
	# Standard methods
	def get_updated_field(self):
		return 'timestamp_mod'
	
	def get_model(self):
		return venue
	
	def index_queryset(self, using=None):
		return self.get_model().objects.filter(timestamp_post__lte=timezone.now()).select_related().prefetch_related('events','events__event')
	
	def prepare(self, obj):
		data = super(venue_index, self).prepare(obj)	# ALWAYS DIFFERENT
		data['_boost'] = 0.8
		return data
	
	
	# Per-field methods
	def prepare_title(self, obj):
		return unicode(obj)
	
	def prepare_item_count(self, obj):
		return obj.events.all().count()

