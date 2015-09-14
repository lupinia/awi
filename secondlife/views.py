# Create your views here.
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from secondlife.models import security_control

@csrf_exempt
@require_POST
def security_response(request, gridname):
	if gridname == 'opensim_lup':
		if request.META.get('HTTP_X_SECONDLIFE_OWNER_NAME','') != 'Natasha Softpaw' or request.META.get('HTTP_X_SECONDLIFE_OBJECT_NAME','') != 'LMC Security Server' or request.META.get('HTTP_X_SECONDLIFE_OWNER_KEY','') != 'adc07b15-c9d5-4ba5-8b64-8cf08d4b0a6f':
			return HttpResponse('ERR')
	
	if gridname == 'sl':
		if request.META.get('HTTP_X_SECONDLIFE_OWNER_NAME','') != 'Natasha Petrichor' or request.META.get('HTTP_X_SECONDLIFE_OBJECT_NAME','') != 'LMC Security Server' or request.META.get('HTTP_X_SECONDLIFE_OWNER_KEY','') != '5edf25ad-8482-4d91-85fe-ed364b486a95':
			return HttpResponse('ERR')
	
	authcheck = security_control.objects.filter(key=request.POST.get('key')).filter(auth=True).filter(grid=gridname)
	if authcheck.exists():
		return HttpResponse('AUTH '+authcheck[0].key+' '+authcheck[0].name)
	else:
		return HttpResponse('NO AUTH')
