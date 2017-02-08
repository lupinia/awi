#	Awi Access (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Context processors
#	=================

from awi_access.models import check_mature

def mature_check(request):
	return {'mature':check_mature(request),}
