#	Awi Access (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Models
#	def access_query:  Returns Q objects corresponding to the access level of the current request.  Example usage:  access_control.objects.filter({main condition}).filter(access_query(request))
#	class access_control:  This is just a meta class to be extended by other models in other apps.
#	=================

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

def access_query(request=False):
	returned_query = models.Q(sites__id = settings.SITE_ID)
	
	if request and request.user.is_authenticated():
		if not request.user.is_superuser or not request.user.is_staff:
			#	Regular User
			published_query = models.Q(published = True) or models.Q(owner = request.user)
			returned_query = returned_query & models.Q(security__lt = 2) & published_query
	else:
		#	Anonymous User
		returned_query = returned_query & models.Q(security__lt = 1) & models.Q(published = True) & models.Q(mature = False)
	
	return returned_query

class access_control(models.Model):
	SECURITY_OPTIONS=((0,'Public'),(1,'Logged-In Users'),(2,'Staff'))
	
	published=models.BooleanField()
	featured=models.BooleanField()
	mature=models.BooleanField()
	security=models.IntegerField(choices=SECURITY_OPTIONS,default=0,blank=True)
	owner=models.ForeignKey(User)
	sites=models.ManyToManyField(Site)
	
	def can_view(self,request=False):
#		Return a tuple; first value is boolean, can view or not.  Second value is an error message if False, empty if True
		public_check = self.is_public()
		if public_check[0]:
			return (True,'')				# If it's public, then can_view is assumed to be true.
		elif not request:
			return (False,'access_norequest')	#	Fail if we can't check the request
		elif request.user.is_superuser:
			return (True,'')				#	Superuser can always view
		elif (not request.user.is_staff and self.security > 1) or (not request.user.is_authenticated() and self.security > 0):
			return (False,'access_perms')	#	If insufficient permissions, show permission error
		elif not self.published and (not request.user.is_staff or self.owner is not request.user):
			return (False,'access_404')		#	If it's unpublished, object only exists if we're staff, or the author.
		elif not self.sites.filter(pk=settings.SITE_ID).exists():
			return (False,'access_404')		#	If we're on the wrong site, object doesn't exist.
		elif self.mature == True and not request.user.is_authenticated():
			return (False,'access_adult')	#	This will be more sophisticated in the future.
		else:
			return (True,'')				#	All access checks passed, show object.
	
	def can_edit(self, request=False, perm_check=''):
#		Return a tuple; first value is boolean, can edit or not.  Second value is an error message if False, empty if True
		if not request:
			return (False,'access_norequest')				#	Fail if we can't check anything
		else:
			access_check = self.can_view(request)
			if request.user.is_superuser:
				return (True,'')				#	Superuser can always edit.
			elif not access_check[0]:
				return access_check				# If we can't view, we can't edit.
			elif perm_check and not request.user.has_perm(perm_check):
				return (False,'access_perms')
			elif self.owner is not request.user:
				return (False,'access_notowner')	# If we're not a superuser, and this isn't our item, we can't edit it.
			else:
				return (True,'')				#	All access checks passed, edit object.
	
	def is_public(self):
#		Returns a tuple.  First value is boolean, indicating whether non-authenticated users can view this or not.  Second value is a list of reasons why not.
		restrictions = []
		public = True
		
		if not self.published:
			public = False
			restrictions.append('Not published')
		if self.security:
			public = False
			restrictions.append('Permissions set to %s' % self.get_security_display())
		if self.mature:
			public = False
			restrictions.append('Mature content')
		
		return (public, restrictions)
	
	class Meta:
		abstract = True