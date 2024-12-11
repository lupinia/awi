# coding=UTF-8
#	DeerCoins (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

import decimal

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class currency(models.Model):
	code = models.SlugField(max_length=1, unique=True, verbose_name='filing code')
	name = models.CharField(max_length=100)
	symbol = models.CharField(max_length=6, null=True, blank=True, help_text='Enter the symbol (such as $) used to represent this currency in shorthand writing.')
	
	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name_plural = 'currencies'

@python_2_unicode_compatible
class country(models.Model):
	code = models.SlugField(max_length=2, unique=True, verbose_name='filing code')
	name = models.CharField(max_length=255)
	flag = models.ImageField(upload_to='flags', null=True, blank=True, verbose_name='flag icon (24px)')
	flag_large = models.ImageField(upload_to='flags-large', null=True, blank=True, verbose_name='flag icon (96px)')
	
	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name_plural = 'countries'

@python_2_unicode_compatible
class gifter(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(unique=True)
	homepage = models.URLField(max_length=255, blank=True, null=True, verbose_name='personal URL', help_text="A link to this person's website or social media account.")
	
	def __str__(self):
		return self.name

@python_2_unicode_compatible
class coin(models.Model):
	code = models.SlugField(unique=True, verbose_name='filing code')
	country = models.ForeignKey(country, on_delete=models.PROTECT)
	country_as_written = models.CharField(max_length=255, blank=True, null=True, verbose_name='country as-written', help_text="Overrides the country name if it's written differently on the coin/note.")
	value = models.DecimalField(max_digits=12, decimal_places=5, blank=True, null=True, help_text='Value of this coin/note relative to its currency.  For example, for 1 cent, enter 0.01.')
	currency = models.ForeignKey(currency, on_delete=models.PROTECT)
	denomination = models.CharField(max_length=60, null=True, blank=True, help_text='Denomination as it appears on the coin/note, if different from the Value field.  For example, a USA $0.25 coin has a denomination of "Quarter Dollar".')
	denomination_code = models.CharField(max_length=6, blank=True, verbose_name='denomination filing code', help_text='Used to generate the overall filing code.  Letting this auto-generate is recommended.')
	is_note = models.BooleanField(verbose_name='note?', help_text='Check this box if this is a banknote/bill instead of a coin.')
	is_special_issue = models.BooleanField(verbose_name='special issue?', help_text='Check this box if this coin/note is commemorative, or a short-term special-issue.')
	year = models.IntegerField(help_text='Gregorian calendar year.')
	year_as_written = models.CharField(max_length=50, blank=True, null=True, verbose_name='year as-written', help_text='If this coin/note represents its year differently from the Gregorian calendar, enter the year and calendar info here.  For example, an Egyptian coin with a year of 1942 would need "1342 (Islamic Calendar)" in this field.')
	
	coin_notes = models.TextField(blank=True, null=True, verbose_name='notes (coin details)', help_text='Details about this coin/note other than condition or how it was acquired.')
	condition_notes = models.TextField(blank=True, null=True, verbose_name='notes (condition)', help_text='Details about the condition of this coin/note')
	
	acquired_from = models.ForeignKey(gifter, blank=True, null=True, on_delete=models.SET_NULL, help_text='If this coin/note was acquired from someone, select that person here.')
	acquired_date = models.DateField(blank=True, null=True)
	acquired_notes = models.TextField(blank=True, null=True, verbose_name='notes (acquisition)', help_text='Details about how and when this coin/note was acquired.')
	
	location_page = models.IntegerField(blank=True, null=True, verbose_name='binder page')
	location_row = models.IntegerField(blank=True, null=True, verbose_name='binder page row')
	location_column = models.IntegerField(blank=True, null=True, verbose_name='binder page column')
	
	detail_link = models.URLField(max_length=255, blank=True, null=True, help_text='Link to an external site (like Numista.com) describing this coin/note in greater detail.')
	
	timestamp_mod = models.DateTimeField(auto_now=True, verbose_name='date/time modified')
	timestamp_post = models.DateTimeField(default=timezone.now, verbose_name='date/time created')
	
	def __str__(self):
		return self.code
	
	@property
	def display_value(self):
		return u'%s%d' % (self.currency.symbol, self.value)
	
	@property
	def display_country(self):
		if self.country_as_written:
			return self.country_as_written
		else:
			return self.country.name
	
	@property
	def display_year(self):
		if self.year_as_written:
			return '%s (%d)' % (self.year_as_written, self.year)
		else:
			return '%d' % self.year
	
	@property
	def location(self):
		if self.location_page:
			loc_text = 'Page %d' % self.location_page
			if self.location_row and self.location_column:
				loc_text = '%s (R%d:C:%d)' % (loc_text, self.location_row, self.location_column)
			elif self.location_row:
				loc_text = '%s (Row %d)' % (loc_text, self.location_row)
			elif self.location_column:
				loc_text = '%s (Column %d)' % (loc_text, self.location_column)
		else:
			return None
	
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
			if self.value < decimal.Decimal(0.01):
				return '%dM' % int(self.value * decimal.Decimal(1000))
			elif self.value < decimal.Decimal(1):
				return '%dC' % int(self.value * decimal.Decimal(100))
			else:
				return '%d' % int(self.value)
		
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
@python_2_unicode_compatible
class code_alias(models.Model):
	code = models.SlugField(unique=True, verbose_name='old filing code')
	coin = models.ForeignKey(coin, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.code
	
	class Meta:
		verbose_name = 'filing code alias'
		verbose_name_plural = 'filing code aliases'

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