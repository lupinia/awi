# coding=UTF-8
#	DeerCoins (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.db import models
from django.conf import settings

class currency(models.Model):
	code = models.SlugField(max_length=1)
	name = models.CharField(max_length=100)
	active_use = models.BooleanField()
	
	def __unicode__(self):
		return self.name

class country(models.Model):
	code = models.SlugField(max_length=2)
	name = models.CharField(max_length=255)
	flag = models.ImageField(upload_to='flags',null=True,blank=True)
	
	def __unicode__(self):
		return self.name

class coin(models.Model):
	code = models.SlugField()
	country = models.ForeignKey(country)
	country_as_written = models.CharField(max_length=255,blank=True,null=True)
	value = models.DecimalField(max_digits=12, decimal_places=5,)
	currency = models.ForeignKey(currency)
	denomination = models.CharField(max_length=60)
	is_note = models.BooleanField()
	is_special_issue = models.BooleanField()
	year = models.IntegerField()
	year_as_written = models.IntegerField()
	
	coin_notes = models.TextField(blank=True,null=True)
	condition_notes = models.TextField(blank=True,null=True)
	
	acquired_from = models.CharField(max_length=255,blank=True,null=True)
	acquired_date = models.DateField(blank=True,null=True)
	acquired_notes = models.TextField(blank=True,null=True)
	
	location_page = models.IntegerField(blank=True,null=True)
	location_row = models.IntegerField(blank=True,null=True)
	location_column = models.IntegerField(blank=True,null=True)
	
	detail_link = models.URLField(max_length=200, blank=True,null=True)
	
	def __unicode__(self):
		return self.code

#	In case a sort code for a coin changes, the old one will still work.
class code_alias(models.Model):
	code = models.SlugField()
	coin = models.ForeignKey(coin)
	
	def __unicode__(self):
		return self.code

#	This model is for a specific project:
#	Trying to acquire Euro coins in every denomination from every country that issues them
class euro(models.Model):
	CHOICES_VALUE = (
		(2, u'€ 2'),
		(1, u'€ 1'),
		(0.5, u'€ 0.50'),
		(0.2, u'€ 0.20'),
		(0.1, u'€ 0.10'),
		(0.05, u'€ 0.05'),
		(0.02, u'€ 0.02'),
		(0.01, u'€ 0.01'),
	)
	CHOICES_COUNTRY = (
		('AD','Andorra'),
		('AT','Austria'),
		('BE','Belgium'),
		('CY','Cyprus'),
		('EE','Estonia'),
		('HI','Finland'),
		('FR','France'),
		('DE','Germany'),
		('GR','Greece'),
		('IE','Ireland'),
		('IT','Italy'),
		('LV','Latvia'),
		('LT','Lithuania'),
		('LU','Luxembourg'),
		('MT','Malta'),
		('MC','Monaco'),
		('NL','Netherlands'),
		('PT','Portugal'),
		('SM','San Marino'),
		('SK','Slovakia'),
		('SI','Slovenia'),
		('ES','Spain'),
		('VA','Vatican City'),
	)
	CHOICES_STATUS = (
		('need','Still needed'),
		('en_route','Promised but not yet received'),
		('acquired','Acquired'),
		('other','Other (see notes)'),
	)
	
	value = models.DecimalField(max_digits=5, decimal_places=2, choices=CHOICES_VALUE)
	country = models.CharField(max_length=3, choices=CHOICES_COUNTRY)
	status = models.CharField(max_length=10, choices=CHOICES_STATUS, default='need')
	coin = models.ForeignKey(coin, blank=True, null=True)
	notes = models.TextField(blank=True, null=True)