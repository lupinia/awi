#	Sunset (Django App)
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Management Command:  process_images
#	Performs a background import of photos, and processes their assets
#	=================

import exiftool
import os.path
import urllib

from django.conf import settings
from django.core.files import File
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone

from datetime import datetime, timedelta
from PIL import Image, ImageOps

from awi_utils.utils import notify
from sunset.models import *

class Command(BaseCommand):
	help = "Rebuilds image assets for new/changed gallery images."
	
	def handle(self, *args, **options):
		try:
			# Priority 1:  Process assets for a new image.
			# Priority 2:  Process assets for an existing image.
			# Priority 3:  Process the oldest folder that hasn't sync'ed in the last X hours (set on next line)
			folder_resync_time = timedelta(hours=24)
			
			# Let's begin!
			# Priority 1:  Process assets for a new image.
			self.log("Checking for new images to process.")
			complete = False
			imagelist = image.objects.filter(rebuild_assets=True, is_new=True).order_by('timestamp_mod').prefetch_related('assets', 'meta')
			if imagelist.exists():
				img = imagelist.first()
				self.log("Processing assets for image %s." % img, image=img)
				complete = self.asset_process(img)
			else:
				# Nothing to do!
				self.log("No new images in need of asset/meta reprocessing.")
			
			# Priority 2:  Process assets for an existing image.
			if not complete:
				self.log("Checking for old images to reprocess.")
				imagelist = image.objects.filter(rebuild_assets=True).order_by('timestamp_mod').prefetch_related('assets', 'meta')
				if imagelist.exists():
					img = imagelist.first()
					self.log("Processing assets for image %s." % img, image=img)
					complete = self.asset_process(img)
				else:
					# Nothing to do!
					self.log("No existing images in need of asset/meta reprocessing.")
			
			# Priority 3:  Process the oldest folder that hasn't sync'ed in the last X hours (set on next line)
			if not complete:
				self.log("Checking for batch folders to sync.")
				import_list = batch_import.objects.filter(Q(timestamp_sync__lt=timezone.now()-folder_resync_time) | Q(timestamp_sync=None)).filter(active=True).order_by('-timestamp_mod','timestamp_sync').prefetch_related('meta', 'images')
				if import_list.exists():
					for to_import in import_list:
						self.log("Checking folder %s." % to_import, batch=to_import)
						import_status = to_import.process_folder()
						if import_status:
							self.log("Successfully imported %d images." % import_status, batch=to_import)
							break
						else:
							self.log("No new images in %s." % to_import, batch=to_import)
					complete = True
				else:
					self.log("No batch folders need to be synchronized.")
			
			self.log("Operation complete.")
		except:
			import sys,traceback
			self.log("An exception occurred:  %s (%s) - %s" % (str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2])), notify_admins=True)
			raise CommandError(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
	
	def log(self, message, notify_admins=False, image=None, batch=None):
		import_log.objects.create(command='manage.process_images', message=message, image=image, batch=batch)
		self.stdout.write(message)
		if notify_admins:
			notify(subject='Sunset - Image Processing Error', msg=message)
	
	def asset_process(self, img):
		# Check if original exists
		# Download original to working directory
		# Parse exif data for original
		# Open original with PIL
		# Create copy of original
		# Create type=thumb and type=bg
		# Watermark copy
		# Create resizes of watermarked copy
		
		# Let's begin!
		# Check if original exists
		original_check = img.get_working_original()
		if original_check:
			# Original exists!  Let's continue.
			self.log("Downloaded original for image %s." % img, image=img)
			
			# Parse exif data for original
			meta_parse_status = img.build_meta()
			if meta_parse_status:
				self.log("Metadata processed for image %s." % img, image=img)
			else:
				self.log("Unable to process metadata for image %s." % img, notify_admins=True, image=img)
			
			# Build derivative assets
			asset_build_status = img.build_assets()
			if asset_build_status:
				built_assets = ', '.join(asset_build_status)
				self.log("Successfully built the following assets for image %s:  %s" % (img,built_assets), image=img)
			else:
				self.log("Unable to build assets for image %s." % img, notify_admins=True, image=img)
			
			if asset_build_status and meta_parse_status:
				self.log("Asset processing complete for image %s." % img, image=img)
				return True
			else:
				return False
		else:
			# No original, so we can't do anything.
			self.log("Original does not exist or could not be retrieved for image %s." % img, notify_admins=True, image=img)
			return False
