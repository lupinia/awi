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
from django.utils import timezone

class currency(models.Model):
	code = models.SlugField(max_length=1, unique=True)
	name = models.CharField(max_length=100)
	symbol = models.CharField(max_length=6,null=True,blank=True)
	
	def __unicode__(self):
		return self.name

class country(models.Model):
	code = models.SlugField(max_length=2, unique=True)
	name = models.CharField(max_length=255)
	flag = models.ImageField(upload_to='flags',null=True,blank=True)
	flag_large = models.ImageField(upload_to='flags-large',null=True,blank=True)
	
	def __unicode__(self):
		return self.name

class gifter(models.Model):
	name = models.CharField(max_length=255)
	code = models.SlugField(unique=True)
	homepage = models.URLField(max_length=255, blank=True,null=True)
	
	def __unicode__(self):
		return self.name

class coin(models.Model):
	code = models.SlugField(unique=True)
	country = models.ForeignKey(country, on_delete=models.PROTECT)
	country_as_written = models.CharField(max_length=255,blank=True,null=True)
	value = models.DecimalField(max_digits=12, decimal_places=5,blank=True,null=True)
	currency = models.ForeignKey(currency, on_delete=models.PROTECT)
	denomination = models.CharField(max_length=60)
	denomination_code = models.CharField(max_length=6, blank=True)
	is_note = models.BooleanField()
	is_special_issue = models.BooleanField()
	year = models.IntegerField()
	year_as_written = models.IntegerField(blank=True,null=True)
	
	coin_notes = models.TextField(blank=True,null=True)
	condition_notes = models.TextField(blank=True,null=True)
	
	acquired_from = models.ForeignKey(gifter,blank=True,null=True, on_delete=models.SET_NULL)
	acquired_date = models.DateField(blank=True,null=True)
	acquired_notes = models.TextField(blank=True,null=True)
	
	location_page = models.IntegerField(blank=True,null=True)
	location_row = models.IntegerField(blank=True,null=True)
	location_column = models.IntegerField(blank=True,null=True)
	
	detail_link = models.URLField(max_length=255, blank=True,null=True)
	
	timestamp_mod=models.DateTimeField(auto_now=True)
	timestamp_post=models.DateTimeField(default=timezone.now)
	
	def __unicode__(self):
		return self.code
	
	def save(self, *args, **kwargs):
		self.denomination_code = self.create_denomination_code()
		
		if not self.code or kwargs.get('rewrite_code',False):
			new_code = self.create_code()
			if new_code:
				if self.code and self.code != new_code:
					code_alias.objects.create(code=self.code, coin=self)
				self.code = new_code
		
		super(coin, self).save(*args, **kwargs)
	
	def create_denomination_code(self):
		if self.value:
			if self.value < 0.01:
				return '%dM' % self.value * 1000
			elif self.value < 1:
				return '%dC' % self.value * 100
			else:
				return '%d' % self.value
		
		else:
			return '0'
	
	def create_code(self):
		new_code = False
		
		if self.denomination_code:
			new_denom_code = self.denomination_code
		else:
			new_denom_code = self.create_denomination_code()
		
		if self.is_note:
			note = 'N'
		else:
			note = 'C'
		
		if not self.country or not self.currency:
			return False
		
		new_code_stem = '%s%s%s%s' % (self.country.code, self.currency.code, note, new_denom_code)
		
		coins_check = coin.objects.filter(code__startswith=new_code_stem)
		if not self in coins_check:
			# If we're here, the code for this coin can be presumed to be unchanged
			code_count = format(coins_check.count()+1, '02d')
			new_code = '%s-%s' % (new_code_stem, code_count)
		
		return new_code

#	In case a sort code for a coin changes, the old one will still work.
class code_alias(models.Model):
	code = models.SlugField(unique=True)
	coin = models.ForeignKey(coin, on_delete=models.CASCADE)
	
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