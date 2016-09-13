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
	'deertrees.*',
	'sunset.*',
	'deerconnect.models.link',
	'django_summernote.*',
)

itemlist_system = (
	'django.contrib.*',
	'awi_error.*',
	'awi_access.*',
	'deerfind.models.pointer',
	'deerfind.models.g2map',
	'deerconnect.models.contact_link',
)

itemlist_misc_exclude = (
	'django.contrib.*',
	'django_processinfo.*',
	'django_summernote.*',
	'awi_error.*',
	'awi_access.*',
	'deerfind.*',
	'deerbooks.*',
	'deertrees.*',
	'deerconnect.*',
	'sunset.*',
)

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
                _('System'),
                models=itemlist_system,
            ),
            items.AppList(
                _('Miscellaneous'),
                exclude=itemlist_misc_exclude,
            ),
            items.MenuItem(_('Server Health'), reverse('admin:django_processinfo_processinfo_changelist')),
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
                [_('Monitor Server Health'), reverse('%s:django_processinfo_processinfo_changelist' % site_name)],
                [_('Change password'), reverse('%s:password_change' % site_name)],
                [_('Log out'), reverse('%s:logout' % site_name)],
            ]
        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Content'),
            models=itemlist_content,
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('Miscellaneous'),
            exclude=itemlist_misc_exclude,
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('System Management'),
            models=itemlist_system,
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(_('Recent Actions'), 5))

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
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _('Recent Actions (This App)'),
                include_list=self.models,
                limit=20
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
