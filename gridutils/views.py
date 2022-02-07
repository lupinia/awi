#	GridUtils - Virtual World Data (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

import simplejson

from dicttoxml import dicttoxml

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views import View

from gridutils.models import avatar, group, region, device
from gridutils.utils import parse_vector, dict_to_apipsv

#	Device API
#	This superclass includes unauthenticated API requests, such as device initialization
class device_api_base(View):
	http_method_names = ['post', 'head', 'options']
	api_input = {}
	api_input_fields = {}
	request_meta = {}
	authenticated = False
	tasklist = {}
	
	device_obj = None
	require_device = False
	
	response_format = 'api'
	response_type = 'text/plain'
	response_data = {}
	
	def setup(self, request, *args, **kwargs):
		super(device_api_base, self).setup(request, *args, **kwargs)
		self.response_format = self.kwargs.get('response_format', 'api')
		if self.response_format == 'json':
			self.response_type = 'application/json'
			self.format_response = self.format_response_json
		elif self.response_format == 'xml':
			self.response_type = 'application/xml'
			self.format_response = self.format_response_xml
		else:
			self.response_type = 'text/plain'
			self.format_response = self.format_response_api
	
	def format_response_json(self):
		return simplejson.dumps(self.response_data)
	
	def format_response_xml(self):
		return dicttoxml(self.response_data, custom_root='device-api')
	
	def format_response_api(self):
		return dict_to_apipsv(self.response_data)
	
	def response(self, httpstatus, **kwargs):
		if httpstatus == 400:
			response_class = HttpResponseBadRequest
		elif httpstatus == 403:
			response_class = HttpResponseForbidden
		else:
			response_class = HttpResponse
		
		return response_class(content=self.format_response(), status=httpstatus, **kwargs)
	
	def parse_headers(self, request):
		parse_status = True
		missing_headers = []
		for header, header_shortname in settings.DEVICE_API_REQUIRED_HEADERS.iteritems():
			meta_value = request.META.get(header, False)
			if meta_value:
				# Special cases:
				if header == 'HTTP_X_SECONDLIFE_REGION' and '(' in meta_value:
					meta_value = meta_value.split(' (')[0]
				elif header == 'HTTP_X_SECONDLIFE_LOCAL_POSITION' and ',' in meta_value:
					self.request_meta['%s_coords' % header_shortname] = parse_vector(meta_value)
				self.request_meta[header_shortname] = meta_value
			else:
				parse_status = False
				missing_headers.append(header)
		
		if len(missing_headers) > 0:
			self.response_data['missing_headers'] = ','.join(missing_headers)
		
		return parse_status
	
	def get_device_queryset(self):
		return device.objects.filter(key=self.request_meta.get('device_key', None)).select_related('owner_account', 'group', 'region', 'region__estate', 'region__estate__grid', 'authorization', 'authorization__parent').prefetch_related('authorization__parent__allowed_users', 'approvals', 'approvals__approver')
	
	def get_device(self):
		device_obj_parent = self.get_device_queryset().first()
		if device_obj_parent:
			self.device_obj = device_obj_parent.get_model()
		
		if self.device_obj or not self.require_device:
			return True
		else:
			return False
	
	def get_api_fields(self):
		# Three levels of priority in the .update() call:
		#	3. Standard fields
		#	2. Device model fields (if present)
		#	1. Per-view/per-endpoint fields
		if self.device_obj:
			base_fields = self.device_obj.api_request_fields
		else:
			base_fields = settings.DEVICE_API_STANDARD_FIELDS
		
		return base_fields.update(self.api_input_fields)
	
	def parse_input(self, request):
		parse_status = True
		missing_fields = []
		for field, required in self.get_api_fields().iteritems():
			field_value = request.POST.get(field, None)
			if field_value is not None:
				self.api_input[field] = field_value
			elif required:
				parse_status = False
				missing_fields.append(field)
		
		if len(missing_fields) > 0:
			self.response_data['missing_fields'] = ','.join(missing_fields)
		
		return parse_status
	
	def over_rate_limit(self):
		rate_limit_key = '%s:%s' % (settings.DEVICE_API_RATELIMIT_CACHE_PREFIX, self.device_obj.key_str)
		if self.device_obj:
			cache_check = cache.get(rate_limit_key)
			if cache_check:
				if cache_check >= self.device_obj.api_rate_limit:
					return True
		
		return False
	
	def increment_rate_limit(self):
		if self.device_obj:
			rate_limit_key = '%s:%s' % (settings.DEVICE_API_RATELIMIT_CACHE_PREFIX, self.device_obj.key_str)
			cache_check = cache.get(rate_limit_key)
			if cache_check:
				try:
					cache.incr(rate_limit_key)
				except ValueError:
					# Corner case: Cached rate limit expired while running this function
					cache.set(rate_limit_key, 1, 60)
			else:
				cache.set(rate_limit_key, 1, 60)
	
	# Main response method: HEAD (unauthenticated)
	def head(self, request, *args, **kwargs):
		if self.parse_headers(request):
			status_code = 204
		else:
			status_code = 400
		
		return self.response(status_code)
	
	# Main response method: POST (unauthenticated)
	def post(self, request, *args, **kwargs):
		# Step 1: Check headers
		if not self.parse_headers(request):
			return self.response(400)
		
		# Step 2: Look up the device
		if not self.get_device():
			return self.response(403)
		
		# Step 3: Check the POST fields
		if not self.parse_input(request):
			return self.response(400)
		
		# This version of the class can't actually do much that's useful
		return self.response(204)


#	All API endpoints should extend this base class
class device_api(device_api_base):
	require_device = True
	
	def get_device_queryset(self):
		return super(device_api, self).get_device_queryset().filter(active=True)
	
	# Pre-authentication security checks
	def authorize_device(self):
		self.authenticated = False
		auth_status = False
		status_code = 403
		if self.device_obj:
			if self.over_rate_limit():
				status_code = 429
			else:
				device_init_status, device_init_reason = self.device_obj.init_status
				if device_init_status:
					# Ok!  We can attempt to authenticate!
					auth_valid = True
					
					# First, make sure the owner matches what we're expecting
					obj_owner_type, obj_owner = self.device_obj.get_owner()
					if self.api_input.get('group_owned', False) and obj_owner_type != 'group':
						auth_valid = False
					elif obj_owner_type == 'group' and not self.api_input.get('group_owned', False):
						auth_valid = False
					elif obj_owner.key_str != self.request_meta['owner_key']:
						auth_valid = False
					elif obj_owner_type != 'group':
						# This isn't really related, but it's more efficient to check this here
						if obj_owner.grid_name.lower() != self.request_meta['owner_name'].lower():
							self.tasklist['owner_name_changed'] = True
					
					# Second, make sure the attachment status matches what we're expecting
					if auth_valid:
						if self.device_obj.wearable_allowed:
							if self.device_obj.attached != self.api_input.get('is_attached', False):
								auth_valid = False
					
					# Next, check the location, if needed
					if auth_valid:
						region_check = self.device_obj.check_region(self.request_meta['region_name'])
						if region_check is False and self.api_input.get('previous_region_name', False):
							# Ok, let's check the corner-case before giving up
							region_check = self.device_obj.check_region(self.api_input.get('previous_region_name', ''))
							if region_check:
								self.tasklist['region_name_changed'] = True
							elif region_check is not None:
								auth_valid = False
							
					# Last, check the device authorization key
					if auth_valid:
						if self.api_input['group_owned'] and self.api_input.get('owner_account_key', False):
							owner_account_key = self.api_input['owner_account_key']
						else:
							owner_account_key = self.request_meta['owner_key']
						
						is_authorized, auth_reason = self.device_obj.authorization.validate(self.api_input['object_auth'], owner_account_key, self.device_obj.key_str)
						if is_authorized:
							auth_status = True
							status_code = 204
						else:
							self.response_data['init_status'] = auth_reason
				
				else:
					self.response_data['init_status'] = device_init_reason
					if device_init_reason == 'new':
						status_code = 401
					elif device_init_reason == 'wait_approval':
						status_code = 425
					elif device_init_reason == 'wait_approved':
						status_code = 400
					else:
						status_code = 403
		
		if not auth_status:
			self.authenticated = False
		
		return (auth_status, status_code)
	
	def authenticate_device(self):
		self.authenticated = False
		is_authorized, status_code = self.authorize_device()
		if is_authorized:
			# Ok!  If we've made it here, every security check has been passed.
			# The only thing left to do is check the password.
			if self.device_obj.check_auth_key(self.api_input['auth_token']):
				# Yay!  Worked so far!
				self.authenticated = True
				
				# Just need to update a few things
				self.increment_rate_limit()
				self.device_obj.set_timestamp_sync()
				
				# Notify the client if the app authorization is expiring
				if self.device_obj.authorization.deprecated:
					self.response_data['init_key_expiration'] = self.device_obj.authorization.timestamp_expire.isoformat()
				
				# Cycle the auth key if needed
				#	(Note: Do this last in case something higher up causes an error)
				if self.device_obj.auth_key_expired:
					self.tasklist['rotate_auth_key'] = True
				
				# All done here!
				return (True, 204)
			
			else:
				self.authenticated = False
				return (False, 401)
		
		else:
			self.authenticated = False
			return (False, status_code)
	
	def update_device(self):
		if self.device_obj and self.authenticated:
			device_changes_pending = False
			
			# First, let's see if the object name changed
			if self.request_meta['device_name'] != self.device_obj.name:
				self.device_obj.name = self.request_meta['device_name']
				self.response_data['device_name_updated'] = self.request_meta['device_name']
				device_changes_pending = True
			
			# Second, let's see if the group has changed
			if self.api_input.get('group_key', False) and not self.device_obj.group_owned:
				if self.api_input['group_key'].lower() == 'none':
					# Object is not currently set to a group
					if self.device_obj.group:
						self.device_obj.group = None
						self.response_data['device_group_removed'] = True
						device_changes_pending = True
				else:
					# Object should be set to a a group
					if not self.device_obj.group or self.api_input['group_key'] != self.device_obj.group.key_str:
						new_group = group.objects.filter(key=self.api_input['group_key']).first()
						if new_group:
							self.device_obj.group = new_group
							self.response_data['device_group_set'] = self.api_input['group_key']
							device_changes_pending = True
						else:
							# This creates a bit of a data integrity problem.
							# We cannot create a new group without knowing its name.
							# However, an LSL script has no way of getting the name of a group,
							# and therefore no way of submitting it via this API.
							# So, we'll use a special token, "_unknown"
							# This will prioritize syncing this group when the data scraper runs.
							grid_obj = self.device_obj.region.estate.grid
							new_group = group.objects.create(key=self.api_input['group_key'], data_incomplete=True, grid=grid_obj, notes='Auto-created by device API.')
							self.device_obj.group = new_group
							self.response_data['device_group_set'] = self.api_input['group_key']
							device_changes_pending = True
			
			# Third, let's check the location
			if not self.device_obj.attached:
				if int(self.request_meta['device_location_coords'][0]) != self.device_obj.location_x:
					self.device_obj.location_x = int(self.request_meta['device_location_coords'][0])
					self.response_data['device_coords_updated'] = True
					device_changes_pending = True
				if int(self.request_meta['device_location_coords'][1]) != self.device_obj.location_y:
					self.device_obj.location_y = int(self.request_meta['device_location_coords'][1])
					self.response_data['device_coords_updated'] = True
					device_changes_pending = True
				if int(self.request_meta['device_location_coords'][2]) != self.device_obj.location_z:
					self.device_obj.location_z = int(self.request_meta['device_location_coords'][2])
					self.response_data['device_coords_updated'] = True
					device_changes_pending = True
			
			# Time to check the tasklist
			# First up, check whether there's been a region name change
			if self.tasklist.get('region_name_changed', False) and self.api_input.get('previous_region_name', False):
				region_obj = self.device_obj.region
				region_obj.name = self.request_meta['region_name']
				region_obj.save()
				self.response_data['device_region_name_updated'] = self.request_meta['region_name']
				self.tasklist['region_name_changed'] = False
			
			# Now check for a username change
			if self.tasklist.get('owner_name_changed', False):
				owner_obj = self.device_obj.owner_account()
				owner_obj.grid_username = self.request_meta['owner_name']
				owner_obj.save()
				self.response_data['device_owner_name_updated'] = self.request_meta['owner_name']
				self.tasklist['owner_name_changed'] = False
			
			# Ok, we're done here, let's tidy up a bit!
			if device_changes_pending:
				self.device_obj.save()
	
	def process_api_request(self, *args, **kwargs):
		# This function is where the meat of the API request goes.
		# It should return an HTTP status code.
		try:
			self.update_device()
		except:
			return 500
		else:
			return 200
	
	# Main response method: POST (unauthenticated)
	def post(self, request, *args, **kwargs):
		# Step 1: Check for an error response from the parent version of this function
		# If we've already failed before even getting here, there's no point in extending the work.
		response_obj = super(device_api, self).post(request, *args, **kwargs)
		if response_obj.status_code != 204:
			return response_obj
		
		# Step 2: Authenticate the request.
		auth_status, auth_status_code = self.authenticate_device()
		if not auth_status:
			return self.response(auth_status_code)
		else:
			self.update_device()
		
		# Step 3: Do the things!
		return self.response(self.process_api_request(*args, **kwargs))
