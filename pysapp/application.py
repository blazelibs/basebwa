from pysmvt.application import WSGIApp
from pysmvt.middleware import full_wsgi_stack
from pysmvt.scripting import application_entry

import config.settings as settingsmod

def make_wsgi(profile='Default'):

    app = WSGIApp(settingsmod, profile)

    # can't run this until after the app is initilized or else the
    # app globals are not setup
    from plugstack.sqlalchemy.lib.middleware import SQLAlchemyApp
    app = SQLAlchemyApp(app)

    return full_wsgi_stack(app)

def script_entry():
    application_entry(make_wsgi)

if __name__ == '__main__':
    script_entry()
