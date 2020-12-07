#	secondlife (Legacy Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Views
#	=================

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from deerguard_sl.models import security_system
from usertools.models import person

# This function will be deprecated as soon as I write a replacement
@csrf_exempt
@require_POST
def security_response(request, system, zone):
	try:
		cur_sys = security_system.objects.filter(slug=system).select_related().prefetch_related('zones','servers').first()
		cur_zone = cur_sys.zones.filter(slug=zone).select_related().first()
		server_check = cur_sys.servers.filter(name=request.META.get('HTTP_X_SECONDLIFE_OBJECT_NAME',''), key=request.META.get('HTTP_X_SECONDLIFE_OBJECT_KEY','')).exists()
		
		if request.META.get('HTTP_X_SECONDLIFE_OWNER_NAME','') != cur_sys.owner.grid_name or request.META.get('HTTP_X_SECONDLIFE_OWNER_KEY','') != cur_sys.owner.key_str or not server_check:
			raise TypeError
		
		cur_user = person.objects.get(key=request.POST.get('key'), grid=cur_sys.grid)
		authcheck = cur_zone.user_allowed(cur_user)
		
		if authcheck:
			return HttpResponse('AUTH %s %s' % (cur_user.key_str, cur_user.grid_name))
		else:
			return HttpResponse('NO AUTH')
	
	except:
		return HttpResponse('ERR')
