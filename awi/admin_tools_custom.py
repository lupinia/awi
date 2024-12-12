#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Custom dashboards and menu for admin_tools module
#	=================

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name
from admin_tools.menu import items, Menu

itemlist_content = (
	'deerbooks.*',
	'sunset.*',
	'deerconnect.models.link',
	'deerattend.*',
	'deercoins.*',
	'deerfood.*',
)

itemlist_structure = (
	'deertrees.*',
	'sunset.models.background_tag',
	'deerconnect.models.contact_link',
)

itemlist_sl = (
	'deerguard_sl.*',
	'deerland.*',
	'gridutils.*',
	'electionmap.*',
)

itemlist_system = (
	'django.contrib.*',
	'awi_access.*',
	'deerfind.*',
	'deerconnect.models.spam_word',
	'deerconnect.models.spam_domain',
	'deerconnect.models.spam_sender',
)

itemlist_misc_exclude = itemlist_content + itemlist_structure + itemlist_system + itemlist_sl

class CustomMenu(Menu):
	def __init__(self, **kwargs):
		Menu.__init__(self, **kwargs)
		self.children += [
			items.MenuItem(u' ', '/'),
			items.MenuItem(_('Dashboard'), reverse('admin:index')),
			items.Bookmarks(),
			items.AppList(
				_('Content'),
				models=itemlist_content,
			),
			items.AppList(
				_('Structure'),
				models=itemlist_structure,
			),
			items.AppList(
				_('Second Life'),
				models=itemlist_sl,
			),
			items.AppList(
				_('System'),
				models=itemlist_system,
			),
			items.AppList(
				_('Miscellaneous'),
				exclude=itemlist_misc_exclude,
			),
		]

	def init_with_context(self, context):
		"""
		Use this method if you need to access the request context.
		"""
		return super(CustomMenu, self).init_with_context(context)


class CustomIndexDashboard(Dashboard):
	"""
	Custom index dashboard for awi-dev.
	"""
	columns=3
	
	def init_with_context(self, context):
		site_name = get_admin_site_name(context)
		# append a link list module for "quick links"
		self.children.append(modules.LinkList(
			_('Quick Links'),
			layout='inline',
			# draggable=False,
			deletable=False,
			# collapsible=False,
			children=[
				[_('Return to site'), '/'],
				[_('Change password'), reverse('%s:password_change' % site_name)],
				[_('Log out'), reverse('%s:logout' % site_name)],
			]
		))

		# append an app list module for "Content"
		self.children.append(modules.AppList(
			_('Content'),
			models=itemlist_content,
		))

		# append an app list module for "Miscellaneous"
		self.children.append(modules.AppList(
			_('Miscellaneous'),
			exclude=itemlist_misc_exclude,
		))

		# append an app list module for "Structure"
		self.children.append(modules.AppList(
			_('Site Structure'),
			models=itemlist_structure,
		))

		# append an app list module for "SL"
		self.children.append(modules.AppList(
			_('Second Life Systems'),
			models=itemlist_sl,
		))

		# append an app list module for "System Management"
		self.children.append(modules.AppList(
			_('System Management'),
			models=itemlist_system,
		))

		# append a recent actions module
		self.children.append(modules.RecentActions(_('Recent Actions'), 10))

		# append a feed module
		# self.children.append(modules.Feed(
			# _('Latest Django News'),
			# feed_url='http://www.djangoproject.com/rss/weblog/',
			# limit=5
		# ))

		# append another link list module for "support".
		# self.children.append(modules.LinkList(
			# _('Support'),
			# children=[
				# {
					# 'title': _('Django documentation'),
					# 'url': 'http://docs.djangoproject.com/',
					# 'external': True,
				# },
				# {
					# 'title': _('Django "django-users" mailing list'),
					# 'url': 'http://groups.google.com/group/django-users',
					# 'external': True,
				# },
				# {
					# 'title': _('Django irc channel'),
					# 'url': 'irc://irc.freenode.net/django',
					# 'external': True,
				# },
			# ]
		# ))


class CustomAppIndexDashboard(AppIndexDashboard):
	"""
	Custom app index dashboard for awi-dev.
	"""

	# we disable title because its redundant with the model list module
	title = ''

	def __init__(self, *args, **kwargs):
		AppIndexDashboard.__init__(self, *args, **kwargs)

		# append a model list module and a recent actions module
		self.children += [
			modules.ModelList(self.app_title, self.get_app_model_classes()),
			modules.RecentActions(
				_('Recent Actions (This App)'),
				include_list=self.get_app_content_types(),
				limit=20
			)
		]

	def init_with_context(self, context):
		"""
		Use this method if you need to access the request context.
		"""
		return super(CustomAppIndexDashboard, self).init_with_context(context)
