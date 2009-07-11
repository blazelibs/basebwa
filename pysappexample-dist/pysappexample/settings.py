from os import path
from werkzeug.routing import Rule
from pysmvt.config import DefaultSettings
from pysutils import prependsitedir
import pysapp.settings

basedir = path.dirname(path.abspath(__file__))
appname = path.basename(basedir)
prependsitedir('..','libs')

class Default(pysapp.settings.Default):
    """ Default settings should be good for production.  User-specific
    development environments can be created below.  """
    
    def __init__(self):
        # call parent init to setup default settings
        pysapp.settings.Default.__init__(self, appname, basedir)
        
        # can be used for display purposes through the app
        self.name.full = 'pysapp-example'
        self.name.short = 'pysapp-example'

        # supporting applications
        self.supporting_apps = ['pysapp', 'pysappexample-sharedmods']
        
        # application modules from our application or supporting applications
        self.modules.misc.enabled = True
        self.modules.helloworld.enabled = True
        self.modules.shorty.enabled = True
        self.modules.announcements.enabled = True
        self.modules.contactform.enabled = True
        self.modules.contentbase.enabled = True
        self.modules.filemanager.enabled = True
        self.modules.newsletter.enabled = True
        self.modules.pyspages.enabled = True

        self.modules.announcements.file_upload.enabled = True
        self.modules.announcements.newsletter.enabled = True
        self.modules.announcements.newsletter.list_id = 1
        
        #######################################################################
        # ROUTING
        #######################################################################
        self.routing.routes.extend([
            # used with pysmvt.routing.style_url|static_url|js_url
            Rule('/', defaults={}, endpoint='misc:Index'),
            Rule('/control-panel', endpoint='apputil:DynamicControlPanel'),
        ])
        
        #######################################################################
        # DATABASE
        #######################################################################
        self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'application.db')

        #######################################################################
        # EMAIL ADDRESSES
        #######################################################################
        # the default 'from' address used if no from address is specified
        self.emails.from_default = 'matt@rcs-comp.com'
        
        # programmers who would get system level notifications (code
        # broke, exception notifications, etc.)
        self.emails.programmers = ['matt@rcs-comp.com']
        
        # people who would get application level notifications (payment recieved,
        # action needed, etc.)
        self.emails.admins = ['matt@rcs-comp.com']
        
        #######################################################################
        # EMAIL SETTINGS
        #######################################################################
        # used by mail_admins() and mail_programmers()
        self.email.subject_prefix = '[%s] ' % appname
        
        #######################################################################
        # EXCEPTION HANDLING
        #######################################################################
        self.exceptions.hide = True
        self.exceptions.email = True
        
        #######################################################################
        # DEBUGGING
        #######################################################################
        self.debugger.enabled = False

class Matt(Default):
    """ this custom "user" class is designed to be used for
    user specific development environments.  It can be used like:

        `pysmvt serve matt`
    """
    def __init__(self):
        Default.__init__(self)

        # a single or list of emails that will be used to override every email sent
        # by the system.  Useful for debugging.  Original recipient information
        # will be added to the body of the email
        self.emails.override = 'matt@rcs-comp.com'

        #######################################################################
        # USERS: DEFAULT ADMIN
        #######################################################################
        self.modules.users.admin.username = 'matt'
        self.modules.users.admin.password = 'password'
        self.modules.users.admin.email = 'matt@rcs-comp.com'

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
# this is just a convenience so we don't have to type the capital letter on the
# command line when running `pysmvt serve`
matt=Matt

class Randy(Default):
    def __init__(self):
        Default.__init__(self)

        # a single or list of emails that will be used to override every email sent
        # by the system.  Useful for debugging.  Original recipient information
        # will be added to the body of the email
        self.emails.override = 'randy@rcs-comp.com'

        #######################################################################
        # USERS: DEFAULT ADMIN
        #######################################################################
        self.modules.users.admin.username = 'randy'
        self.modules.users.admin.password = 'password'
        self.modules.users.admin.email = 'randy@rcs-comp.com'

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
# this is just a convenience so we don't have to type the capital letter on the
# command line when running `pysmvt serve`
randy=Randy
