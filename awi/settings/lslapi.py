#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - LSL API
#	Configuration for the GridUtils virtual device/LSL script API
#	=================

#	Number of days in the future to expire an authorization token when replacing it
DEVICE_AUTH_DEPRECATION_DAYS = 365

#	Number of hours in the future to expire a device manual approval request after creating it
DEVICE_APPROVAL_REQUEST_MAXAGE = 24

#	Dictionary of required headers for device API requests, and more standardized internal names
DEVICE_API_REQUIRED_HEADERS = {
	'HTTP_X_SECONDLIFE_OBJECT_NAME': 'device_name',
	'HTTP_X_SECONDLIFE_OBJECT_KEY': 'device_key',
	'HTTP_X_SECONDLIFE_OWNER_NAME': 'owner_name',
	'HTTP_X_SECONDLIFE_OWNER_KEY': 'owner_key',
	'HTTP_X_SECONDLIFE_SHARD': 'grid_shard',
	'HTTP_X_SECONDLIFE_REGION': 'region_name',
	'HTTP_X_SECONDLIFE_LOCAL_POSITION': 'device_location',
}

#	API rate limiting
DEVICE_API_RATELIMIT_DEFAULT = 6	# Queries per minute per device UUID if not authenticated
DEVICE_API_CACHE_PREFIX = 'gudvcapi'
#DEVICE_API_CACHE_PREFIX = 'gudvcapi_devicereq_open'
#DEVICE_API_INITLIMIT_CACHE_PREFIX = 'gudvcapi_deviceinit_open'
DEVICE_API_INITLIMIT = 60*60*24  # 24 hours

#	Dictionary of expected POST fields for all device API requests, and whether they're required
#		If True, validation will fail without this field
DEVICE_API_STANDARD_FIELDS = {
	'auth_token': True,
	'app_auth': True,
	'group_owned': True,
	
	'is_attached': False,	# This shouldn't be present in most requests, but checking it anyway is useful for security
	'group_key': False,
	'owner_account_key': False,
	'previous_region_name': False,	# Only used for a corner case where a region is renamed
}

#	This dictionary stores the settings for different types of Second Life/OpenSim objects
#	Use the app name and model name of the parent model to reference these.
#	Structure:
#		appname.modelname:
#			confirm_new:  If True, user attempting to initialize a new object will be required to login to the website to verify the request.
#			limit_duplicates:  If True, only one device of the same type per user may be rezzed in each region.
#			limit_move:  If True, the same object UUID with the same auth token in a different region will be blocked.  Otherwise, rezzing this device in a new region will update the existing device, deactivating the old one.
#			require_url:  If True, a valid remote URL for the in-world device will be expected and maintained.
#			wearable_allowed:  If True, instances of this device can have their "wearable" attribute set to True, which will bypass location checks entirely.  Use carefully!
#			auth_key_maxage:  Number of days to wait before the next request will cycle the auth key.
#			sync_age_yellow:  Number of days to wait before the sync health is a cause for concern (the "red" status is defined by timestamp_sync older than now - auth_key_maxage).
#			api_rate_limit:  Maximum number of queries per device per minute.
#			standard_fields:  Optional.  Follows the structure of DEVICE_API_STANDARD_FIELDS.
DEVICE_SETTINGS = {
	'gridutils.device': {	# Defaults
		'confirm_new': False,
		'limit_duplicates': False,
		'limit_move': True,
		'require_url': False,
		'wearable_allowed': False,
		'auth_key_maxage': 14,
		'sync_age_yellow': 7,
		'api_rate_limit': 30,
	},
	# DeerGuard
	'deerguard_sl.security_server': {
		'confirm_new': True,
		'limit_duplicates': False,
		'limit_move': True,
		'require_url': False,
		'wearable_allowed': False,
		'auth_key_maxage': 30,
		'sync_age_yellow': 14,
		'api_rate_limit': 60,
	},
}

