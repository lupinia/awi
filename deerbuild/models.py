#	DeerBuild - Virtual World Creator Tools (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	=================

from django.core.urlresolvers import reverse
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from awi.utils.models import TimestampModel
from awi.utils.rand import rand_char_list, rand_int_list
from awi.utils.types import is_int

@python_2_unicode_compatible
class license_plate_region_group(TimestampModel):
	name = models.CharField(max_length=200)
	slug = models.SlugField(null=False)
	
	notes = models.TextField(blank=True, null=True)
	active = models.BooleanField(default=True, blank=True, db_index=True)
	
	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('deerbuild:plategen_list', kwargs={'group':self.slug})
	
	@property
	def is_active(self):
		return self.active
	
	class Meta:
		verbose_name = 'plate region group'
		ordering = ['slug',]


@python_2_unicode_compatible
class license_plate_region(TimestampModel):
	name = models.CharField(max_length=200)
	code = models.CharField(max_length=4, validators=[MinLengthValidator(4)], db_index=True, unique=True)
	group = models.ForeignKey(license_plate_region_group, on_delete=models.PROTECT, related_name='plate_regions')
	
	notes = models.TextField(blank=True, null=True)
	active = models.BooleanField(default=True, blank=True, db_index=True)
	
	def __str__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		self.code = self.code.upper()
		super(license_plate_region, self).save(*args, **kwargs)
	
	@property
	def is_active(self):
		if self.active:
			return self.group.active
		else:
			return self.active
	
	class Meta:
		verbose_name = 'plate region'
		ordering = ['code',]


@python_2_unicode_compatible
class license_plate(TimestampModel):
	design_name = models.CharField(max_length=200)
	territory = models.ForeignKey(license_plate_region, on_delete=models.CASCADE, related_name='plates')
	design_code = models.CharField(max_length=2, validators=[MinLengthValidator(2)], db_index=True, verbose_name='design code')
	can_generate = models.BooleanField(default=True, blank=True)
	sequence = models.CharField(max_length=12, help_text='Use the following special characters to define random sequences: # == Number (0-9), + == Non-zero number (1-9), ? == Letter, * == Letter or number, all other characters will be literal')
	
	notes = models.TextField(blank=True, null=True)
	active = models.BooleanField(default=True, blank=True, db_index=True)
	
	@property
	def code(self):
		return '%s-%s' % (self.territory.code, self.design_code)
	
	@property
	def name(self):
		return '%s - %s' % (self.territory.name, self.design_name)
	
	def get_absolute_url(self):
		return reverse('deerbuild:plategen', kwargs={'group':self.territory.group.slug, 'territory':self.territory.code, 'code':self.design_code})
	
	def __str__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		self.design_code = self.design_code.upper()
		super(license_plate, self).save(*args, **kwargs)
	
	@property
	def is_active(self):
		if self.active:
			if self.territory.active:
				return self.territory.group.active
			else:
				return self.territory.active
		else:
			return self.active
	
	@property
	def sample(self):
		"""Basic sample version of the plate sequence"""
		return self.sequence.replace('#','0').replace('+','9').replace('?','A')
	
	@property
	def chars_total(self):
		"""Total length of the sequence"""
		return len(self.sequence)
	
	def generate(self):
		"""
		Generate a new random license plate based on the sequence string.
		Each character in the sequence string will be replaced individually, 
		so the length of the sequence defines the length of the returned string. 
		
		Special characters:
			#: Number (0-9)
			+: Non-Zero Number (1-9)
			?: Letter (excluding I or O)
			*: Letter or number (0-9), excluding I or O
		
		Any other characters in the sequence will treated as literal and not replaced. 
		This includes specific letters and numbers, or spaces and hyphens.
		"""
		if not self.can_generate:
			# If we're not supposed to be generating random sequences, always return the sample
			return self.sample
		
		plate_number = []
		prev_char = None
		prev_digit = None
		for char in self.sequence:
			
			# Check for digits first
			if char == '#' or char == '+':
				no_zero = False
				exclude_list = []
				if char == '+':
					no_zero = True
				
				if prev_digit is not None:
					# Avoid duplicates
					exclude_list = [prev_digit]
				
				new_digit = rand_int_list(1, exclude_zero=no_zero, first_zero=True, exclude=exclude_list)[0]
				prev_digit = new_digit
				plate_number.append(str(new_digit))
			
			# If it's not a number, maybe it's a letter?
			elif char == '?' or char == '*':
				digits = False
				exclude_list = ['i', 'o']
				if prev_char is not None:
					exclude_list.append(prev_char)
				
				if char == '*':
					digits = True
					
					# Exclusion corner-case:  Need to also exclude prev_digit
					if prev_digit is not None:
						exclude_list.append(str(prev_digit))
				
				new_char = rand_char_list(1, exclude=exclude_list, include_digits=digits)[0]
				prev_char = new_char
				plate_number.append(new_char)
				
				# Corner case: If this is a digit, we also need to exclude it from number checks
				if char == '*' and is_int(new_char):
					prev_digit = int(new_char)
			
			# Must be a literal, then
			else:
				plate_number.append(char)
				prev_char = char
				if is_int(char):
					prev_digit = int(char)
		
		# All done!
		return ''.join(plate_number)
	
	class Meta:
		verbose_name = 'license plate'
		unique_together = ('design_code', 'territory',)
		ordering = ['territory__code', 'design_code',]
