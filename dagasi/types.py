#	Dagasi - Content Security (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Data Types
#	=================

from django.conf import settings

from awi.utils import types as typeutils

class status(object):
	"""
	Defines the outcome of a security check
	Primarily behaves as a bool
	"""
	
	_outcome = False
	_reasons = []
	
	def __init__(self, *args, **kwargs):
		"""
		status(outcome, reason) -> Create a new status object
		"""
		
		need_outcome = True
		need_reason = True
		# Let's start with the kwargs, because they're easy
		if 'outcome' in kwargs.keys():
			self.outcome = kwargs.pop('outcome', self.outcome)
			need_outcome = False
		
		if 'reason' in kwargs.keys():
			self.reason = kwargs.pop('reason', self.reason)
			need_reason = False
		elif 'reasons' in kwargs.keys():
			self.reasons = kwargs.pop('reasons', self.reasons)
			need_reason = False
		
		if args and any([need_outcome, need_reason]):
			# Ok, we still have positional arguments to deal with
			# And we still *need* positional arguments, so let's parse them!
			args = list(args)
			if isinstance(args[0], status):
				# This is converting one status to another
				self.outcome = args[0].outcome
				self.reasons = args[0].reasons
				args.pop(0)
				need_outcome = False
				need_reason = False
			
			elif len(args) == 1:
				if need_outcome:
					self.outcome = args[0]
					args = []
				elif need_reason:
					self.reason = args[0]
					args = []
			
			elif len(args) > 1:
				if need_outcome:
					self.outcome = args.pop(0)
					
				if need_reason:
					self.reason = args.pop(0)
		
		super(status, self).__init__(*args, **kwargs)
	
	
	# Primary security check outcome
	@property
	def outcome(self):
		"""Outcome of a security check, True if passed, False if failed"""
		return self._outcome
	
	@outcome.setter
	def outcome(self, newval):
		self._outcome = bool(newval)
	
	@outcome.deleter
	def outcome(self):
		self._outcome = False
	
	
	# Reason code for this outcome
	@property
	def reason(self):
		"""
		Primary reason for this security check result
		There can be more than one, but this is always the most recent
		Use status.reasons to get all of them
		Always returns a string if outcome is False
			Use status.has_reason to test whether this is actually blank
		Returns None if there are no reasons and outcome is True
		"""
		if self._reasons:
			# These have to be added in reverse order because of Python reasons
			# Therefore, the last element is the most recent
			return self._reasons[-1]
		elif self.outcome:
			return None
		else:
			return 'access_unknown'
	
	@reason.setter
	def reason(self, newval):
		return self._set_reasons(newval)
	
	@reason.deleter
	def reason(self):
		self._reasons = []
	
	@property
	def reasons(self):
		"""All reasons for this security check result, as a list"""
		return self._reasons
	
	@reasons.setter
	def reasons(self, newval):
		return self._set_reasons(newval)
	
	def _set_reasons(self, newval):
		"""Reusable setter for both types of reason access"""
		if typeutils.is_string(newval):
			self._reasons.append(newval)
		elif typeutils.is_iterable(newval):
			self._reasons = self._reasons + newval
		else:
			raise TypeError('reason must be string or list')
	
	@property
	def has_reason(self):
		"""Returns true if a reason has been set"""
		return bool(self.reason_count)
	
	@property
	def reason_count(self):
		"""Number of reason codes attached to this status"""
		return len(self._reasons)
	
	def update(self, outcome=False, reason=None):
		"""Set both parameters fresh, without reinitializing"""
		self.outcome = outcome
		if reason:
			self.reason = reason
		
		return self
	
	# OUTPUT
	def as_tuple(self):
		"""Old-style behavior, returns outcome and reason as a tuple"""
		return (self.outcome, self.reasons)
	
	# LOGIC OPERATORS
	def __bool__(self):
		return bool(self.outcome)
	
	def __nonzero__(self):
		return self.__bool__()
	
	def __not__(self):
		return not self.__bool__()
	
	
	# TYPECASTING
	def __repr__(self):
		if self.reason_count > 1:
			return 'status(%s, ["%s"])' % (str(self.outcome), '", "'.join(self.reasons))
		elif self.has_reason:
			return 'status(%s, "%s")' % (str(self.outcome), self.reason)
		else:
			return 'status(%s)' % str(self.outcome)
	
	def __str__(self):
		return self.as_string(pad=True)
