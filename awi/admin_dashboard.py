"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'awi-dev.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'awi-dev.dashboard.CustomAppIndexDashboard'
"""

#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Custom dashboard for admin_tools module
#	TODO:  Merge admin_tools.py and admin_dashboard.py
#	=================

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name


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
            models=('deerbooks.*','deertrees.*','django_summernote.*',),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('Miscellaneous'),
            exclude=('django.contrib.*','awi_error.*','awi_bg.*','awi_access.*','deerfind.*','django_processinfo.*',
                     'deerbooks.*','deertrees.*','django_summernote.*',),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('System Management'),
            models=('django.contrib.*','awi_error.*','awi_bg.models.background','awi_access.*','deerfind.models.pointer',),
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
