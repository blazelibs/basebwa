# -*- coding: utf-8 -*-
from os import path
from werkzeug.routing import Rule
from pysmvt.config import DefaultSettings

class Default(DefaultSettings):
    
    def __init__(self, *args):
        DefaultSettings.__init__(self, *args)
        
        # name of this webapp
        self.name.full = 'RCS App Base'
        self.name.short = 'rcsappbase'
        
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
        
        #######################################################################
        # SYSTEM VIEW ENDPOINTS
        #######################################################################
        self.endpoint.sys_error = 'apputil:SystemError'
        self.endpoint.sys_auth_error = 'apputil:AuthError'
        self.endpoint.bad_request_error = 'apputil:BadRequestError'
        
        #######################################################################
        # EMAIL ADDRESSES
        #######################################################################
        # the default 'from' address used if no from address is specified
        self.emails.from_default = 'webprogramming@rcs-comp.com'
        # programmers who would get system level notifications (code
        # broke, exception notifications, etc.)
        self.emails.programmers = ['webprogramming@rcs-comp.com']
        
        #######################################################################
        # ERROR DOCUMENTS
        #######################################################################
        self.error_docs[400] = 'apputil:BadRequestError'
        self.error_docs[401] = 'apputil:AuthError'
        self.error_docs[403] = 'apputil:Forbidden'
        self.error_docs[404] = 'apputil:NotFoundError'
        self.error_docs[500] = 'apputil:SystemError'

