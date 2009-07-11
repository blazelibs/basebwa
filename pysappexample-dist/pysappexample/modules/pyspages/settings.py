# -*- coding: utf-8 -*-
from werkzeug.routing import Rule
from pysmvt.config import QuickSettings

class Settings(QuickSettings):

    def __init__(self):
        QuickSettings.__init__(self)

        self.routes = [
            Rule('/content.html', defaults={'page': 'content.html'}, endpoint='pyspages:ServePage'),
        ]
