# -*- coding: utf-8 -*-
from datetime import timedelta
from os import path
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.routing import Rule
from pysmvt.config import DefaultSettings

class Default(DefaultSettings):
    
    def __init__(self, appname=None, basedir=None):
        
        # most of the time, these values will be based from applications
        # higher in the stack, but pysapp also needs to work as a standalone
        # application
        if not basedir or not appname:
            basedir = path.dirname(path.abspath(__file__))
            appname = path.basename(basedir)
            is_primary = True
        else:
            is_primary = False
        DefaultSettings.__init__(self, appname, basedir)
        
        self.name.full = 'pysapp application'
        self.name.short = 'pysapp app'
        
        # application modules from our application or supporting applications
        self.modules.users.enabled = True
        self.modules.apputil.enabled = True
        
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
        # SYSTEM VIEW ENDPOINTS
        #######################################################################
        self.endpoint.sys_error = 'apputil:SystemError'
        self.endpoint.sys_auth_error = 'apputil:AuthError'
        self.endpoint.bad_request_error = 'apputil:BadRequestError'
        
        #######################################################################
        # ERROR DOCUMENTS
        #######################################################################
        self.error_docs[400] = 'apputil:BadRequestError'
        self.error_docs[401] = 'apputil:AuthError'
        self.error_docs[403] = 'apputil:Forbidden'
        self.error_docs[404] = 'apputil:NotFoundError'
        self.error_docs[500] = 'apputil:SystemError'
        
        #######################################################################
        # TESTING
        #######################################################################
        self.testing.init_callables = 'testing.setup_db_structure'

    def turn_on_sql_logging(self):
        sl = logging.getLogger('sqlalchemy.engine')
        sl.setLevel(logging.INFO)
        format_str = "%(asctime)s - %(message)s"
        formatter = logging.Formatter(format_str)
        app_handler = RotatingFileHandler(
            path.join(self.dirs.logs, 'sql.log'),
              maxBytes=self.logs.max_bytes,
              backupCount=self.logs.backup_count,
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(formatter)
        sl.addHandler(app_handler)
    
    def setup_beaker_db_sessions(self, timeout=60*60*12, cookie_expires=timedelta(weeks=10)):
        #http://beaker.groovie.org/configuration.html
        self.beaker.type = 'ext:database'
        self.beaker.cookie_expires = cookie_expires
        self.beaker.timeout = timeout
        self.assign_beaker_url()
    
    def assign_beaker_url(self):
        self.beaker.url = self.db.url

class Dev(Default):
    """ this custom "user" class is designed to be used for
    user specific development environments.  It can be used like:
    
        `pysmvt serve dev`
    """
    def __init__(self):
        Default.__init__(self)
        
        #######################################################################
        # EMAIL SETTINGS
        #######################################################################
        # a single or list of emails that will be used to override every email sent
        # by the system.  Useful for debugging.  Original recipient information
        # will be added to the body of the email
        #self.emails.override = 'devemail@example.com'
        
        # if using emails, this must be set
        #self.emails.from_default = 'devemail@example.com'
        
        #######################################################################
        # USERS: DEFAULT ADMIN
        # --------------------------------------------------------------------
        #
        # This section is used when `pysmvt users_initmod` or
        # `pysmvt broadcast initmod` is used to create the default user.
        # If left commented out, you will be promted for the information.
        #
        #######################################################################
        #self.modules.users.admin.username = 'devuser'
        #self.modules.users.admin.password = 'MSsfej'
        #self.modules.users.admin.email = 'devemail@example.com'
        
        #######################################################################
        # EXCEPTION HANDLING
        #######################################################################
        self.exceptions.hide = False
        self.exceptions.email = False
        
        #######################################################################
        # DEBUGGING
        #######################################################################
        self.debugger.enabled = True
        # this is a security risk on a live system, so we only turn it on
        # for a specific user config
        self.debugger.interactive = True
    
    def apply_test_settings(self):
        #######################################################################
        # EMAIL SETTINGS
        #######################################################################
        # if using emails, this must be set
        self.emails.from_default = 'devemail@example.com'
        
        #######################################################################
        # TEMPLATES
        #######################################################################
        # use test template instead of real templates to speed up the tests
        self.template.default = 'test.html'
        self.template.admin = 'test.html'

        #######################################################################
        # DATABASE
        #######################################################################
        # in memory sqlite DB is the fastest
        self.db.url = 'sqlite://'
        # uncomment this if you want to use a database you can inspect
        #self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'test_application.db')
        
        #######################################################################
        # DEBUGGING
        #######################################################################
        # turn off the debugger or all exceptions will get turned into
        # 500 SERVER ERROR responses when testing, which makes things VERY
        # difficult to troubleshoot
        self.debugger.enabled = False
# this is just a convenience so we don't have to type the capital letter on the
# command line when running `pysmvt serve dev`
dev = Dev

class Test(Dev):
    """ default profile when running tests """
    def __init__(self):
        # call parent init to setup default settings
        Dev.__init__(self)
        self.apply_test_settings()
test=Test

# often times, you will need developer or computer specific configurations
# that you don't want to be part of the main settings file (because it clutters
# up the file).  Therefore, we can conditionally include a site-specific
# settings file with the profiles needed at only that site.  We do it at the
# bottom of this file to allow the site-specific file to inherit items from this
# file:

try:
    from site_settings import *
except ImportError, e:
    if 'No module named site_settings' not in str(e):
        raise
    
## Example site_settings.py file:
#from settings import Dev as SettingsDev
#
#class Dev(SettingsDev):
#    """ this custom "user" class is designed to be used for
#    user specific development environments.  It can be used like:
#    
#        `pysmvt serve dev`
#    """
#    def __init__(self):
#        SettingsDev.__init__(self)
#        self.emails.override = 'rsyring@inteli-com.com'
#        self.emails.from_default = 'rsyring@inteli-com.com'
#dev = Dev
#
# have to redefine this so its based on the correct class object
#class Test(Dev):
#    """ default profile when running tests """
#    def __init__(self):
#         call parent init to setup default settings
#        Dev.__init__(self)
#        self.apply_test_settings()
#test=Test