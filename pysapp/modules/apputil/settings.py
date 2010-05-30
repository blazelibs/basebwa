# -*- coding: utf-8 -*-

from werkzeug.routing import Rule
from pysmvt.config import QuickSettings

class Settings(QuickSettings):

    def __init__(self):
        QuickSettings.__init__(self)


        self.routes = [
            Rule('/system-error', endpoint='apputil:SystemError'),
            Rule('/blank-page', endpoint='apputil:BlankPage'),
            Rule('/authorization-error', endpoint='apputil:AuthError'),
            Rule('/bad-request', endpoint='apputil:BadRequestError'),
            Rule('/forbidden', endpoint='apputil:Forbidden'),
            Rule('/apputil/test-form', endpoint='apputil:TestForm'),
            Rule('/apputil/test-form-static', defaults={'is_static':True}, endpoint='apputil:TestForm')
        ]
