from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

class access_control(models.Model):
	SECURITY_OPTIONS=((0,'Public'),(1,'Logged-In Users'),(2,'Staff'))
	
	published=models.BooleanField()
	featured=models.BooleanField()
	mature=models.BooleanField()
	security=models.IntegerField(choices=SECURITY_OPTIONS,default=0,blank=True)
	owner=models.ForeignKey(User)
	sites=models.ManyToManyField(Site)
	
	def can_view(self,request=False):
		from django.conf import settings
		
#		Return a tuple; first value is boolean, can view or not.  Second value is an error message if False, empty if True
		if not request:
			return (False,'')				#	Fail if we can't check anything
		elif request.user.is_superuser:
			return (True,'')				#	Superuser can always view
		elif (not request.user.is_staff and self.security > 1) or (not request.user.is_authenticated() and self.security > 0):
			return (False,'access_perms')	#	If insufficient permissions, show permission error
		elif not self.published and (not request.user.is_staff or self.owner is not request.user):
			return (False,'access_404')		#	If it's unpublished, object only exists if we're staff, or the author.
		elif not self.sites.filter(id=settings.SITE_ID).exists():
			return (False,'access_404')		#	If we're on the wrong site, object doesn't exist.
		elif self.mature == True and not request.user.is_authenticated():
			return (False,'access_adult')	#	This will be more sophisticated in the future.
		else:
			return (True,'')				#	All access checks passed, show object.
	
	class Meta:
		abstract = True