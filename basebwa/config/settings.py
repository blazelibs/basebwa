from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler
from os import path

from blazeweb.config import DefaultSettings
from werkzeug.routing import Rule

basedir = path.dirname(path.dirname(__file__))
app_package = path.basename(basedir)

class Default(DefaultSettings):

    def init(self, ap=None, bd=None):
        # most of the time, these values will be based from applications
        # higher in the stack, but basebwa also needs to work as a standalone
        # application
        if ap and bd:
            self.dirs.base = bd
            self.app_package = ap
            is_primary = False
        else:
            self.dirs.base = basedir
            self.app_package = app_package
            is_primary = True
        DefaultSettings.init(self)

        self.name.full = 'basebwa application'
        self.name.short = 'basebwa app'

        if is_primary:
            self.init_components()

        #######################################################################
        # ROUTING
        #######################################################################
        self.routing.routes = [
            Rule('/<file>', endpoint='static', build_only=True),
            Rule('/c/<file>', endpoint='styles', build_only=True),
            Rule('/js/<file>', endpoint='javascript', build_only=True),
        ]
        if is_primary:
            self.routing.routes.extend([
                Rule('/', defaults={}, endpoint='apputil:HomePage'),
                Rule('/control-panel', endpoint='apputil:DynamicControlPanel'),
            ])

        #######################################################################
        # TEMPLATES
        #######################################################################
        self.template.admin = 'admin.html'

        ################################################################
        # DATABASE
        #######################################################################
        self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'application.db')
        self.db.echo = False

        #######################################################################
        # CONTROL PANEL
        #######################################################################
        self.cp_nav_sections = []

        #######################################################################
        # BEAKER SESSIONS
        #######################################################################
        self.init_beaker()

    def init_components(self, common=True, sqlalchemy=True, auth=True, apputil=True, datagrid=True):
        # application modules from our application or supporting applications
        if common:
            self.add_component(app_package, 'common', 'commonbwc')
        if sqlalchemy:
            self.add_component(app_package, 'sqlalchemy', 'sqlalchemybwc')
        if auth:
            self.add_component(app_package, 'auth', 'authbwc')
        if apputil:
            self.add_component(app_package, 'apputil')
        if datagrid:
            self.add_component(app_package, 'datagrid', 'datagridbwc')

    def init_beaker(self, timeout=60*60*12, cookie_expires=timedelta(weeks=10)):
        #http://beaker.groovie.org/configuration.html
        self.beaker.type = 'ext:database'
        self.beaker.cookie_expires = cookie_expires
        self.beaker.timeout = timeout
        self.assign_beaker_url()

    def assign_beaker_url(self):
        self.beaker.url = self.db.url

    def apply_dev_settings(self, override_email, admin_user, admin_pass):

        #######################################################################
        # USERS: DEFAULT ADMIN
        #######################################################################
        self.components.auth.admin.username = admin_user
        self.components.auth.admin.password = admin_pass
        self.components.auth.admin.email = override_email

        DefaultSettings.apply_dev_settings(self, override_email)

    def apply_test_settings(self, testing_layouts=True):
        #######################################################################
        # TEMPLATES
        #######################################################################
        # use test template instead of real templates to speed up the tests
        if testing_layouts:
            self.template.default = 'common:layout_testing.html'
            self.template.admin = 'common:layout_testing.html'

        #######################################################################
        # DATABASE
        #######################################################################
        # in memory sqlite DB is the fastest
        self.db.url = 'sqlite://'
        self.assign_beaker_url()

        DefaultSettings.apply_test_settings(self)

try:
    from site_settings import *
except ImportError, e:
    if 'No module named site_settings' not in str(e):
        raise
