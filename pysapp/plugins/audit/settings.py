# -*- coding: utf-8 -*-
from werkzeug.routing import Rule
from pysmvt.config import QuickSettings

class Settings(QuickSettings):

    def __init__(self):
        QuickSettings.__init__(self)

        self.routes = [
            Rule('/audit', endpoint='audit:Index'),
        ]