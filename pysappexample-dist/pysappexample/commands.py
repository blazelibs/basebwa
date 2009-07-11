#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pysmvt import modimport, db

def action_webapp_initapp():
    """ initialize all application level data for the application """
    # initialize db session
    db.sess = db.Session()

    attr_add = modimport('contentbase.actions', 'attr_add')
    list_add = modimport('newsletter.actions', 'list_add')
    contact_add = modimport('contactform.actions', 'contact_add')
    group_perm_init = modimport('users.actions', 'permission_assignments_group_by_name')

    # admin group init
    admin_perm_list = [ u'announcements-manage',
                        u'contactform-manage',
                        u'file-manage',
                        u'newsletter-manage',
                        u'webapp-controlpanel',
                      ]
    group_perm_init(u'admin', admin_perm_list)

    # announcements
    attr_add(catname=u'announcement-categories', name=u'general', display=u'General', inactive=False, safe='unique')
    # contact form contacts
    contact_add(name=u'Randy', name_url_slug=u'randy', email_address=u'randy@rcs-comp.com', safe='unique')
    contact_add(name=u'Matt', email_address=u'matt@rcs-comp.com', safe='unique')
    # the newsletter list
    list_add(name=u'Test List', safe='unique')
    # file manage categories
    attr_add(catname=u'file-categories', name=u'cat-1', display=u'Test Category 1', inactive=False, safe='unique')
    attr_add(catname=u'file-categories', name=u'cat-2', display=u'Test Category 2', inactive=False, safe='unique')

broadcast_initapp = action_webapp_initapp
