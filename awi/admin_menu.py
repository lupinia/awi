"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'awi-dev.menu.CustomMenu'
"""

#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Custom menu for admin_tools module
#	TODO:  Merge admin_tools.py and admin_dashboard.py
#	=================

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from admin_tools.menu import items, Menu


class CustomMenu(Menu):
    """
    Custom Menu for awi-dev admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(u' ', '/'),
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.Bookmarks(),
            items.AppList(
                _('Content'),
                models=('deertrees.*','django_summernote.*',),
            ),
            items.AppList(
                _('System'),
                models=('django.contrib.*','awi_error.*','awi_bg.models.background','awi_access.*','deerfind.models.pointer'),
            ),
            items.AppList(
                _('Miscellaneous'),
                exclude=('django.contrib.*','awi_error.*','awi_bg.*','awi_access.*','deerfind.*','django_processinfo.*',
                         'deertrees.*','django_summernote.*',),
            ),
            items.MenuItem(_('Server Health'), reverse('admin:django_processinfo_processinfo_changelist')),
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomMenu, self).init_with_context(context)
