import sys
from os import remove

import elixir
from paste.fixture import TestApp
from pysmvt import settings, db
from pysmvt.commands import manual_broadcast
from pysmvt.script import testprep
from ..applications import make_wsgi

testprep()
# setup test DB only once
app = make_wsgi('Test')

class BaseTest(object):
    app = None
    
    @classmethod
    def setup_class(cls):
        try:
            if settings.test.dbfile:
                remove(settings.test.dbfile)
        except (AttributeError, WindowsError):
            pass
        # this is required b/c the model won't work correctly with multiple apps
        def inits():
            manual_broadcast('initdb')
            manual_broadcast('initapp')
            manual_broadcast('initmod')
        app({'pysapp.callable_dispatch': inits}, lambda s,h: None)
        cls.app = TestApp(app)
    
    @classmethod
    def teardown_class(cls):
        db.meta.drop_all(bind=db.engine)
        cls.app = None        

class AdminBaseTest(BaseTest):
    
    # the first time this class is used, the admin user will need to change
    # their password on login
    first = True
    
    @classmethod
    def setup_class(cls):
        BaseTest.setup_class()
        
        r = cls.app.get('/users/login')
        form = r.forms[0]
        
        form['login_id'] = 'admin'
        
        if cls.first:
            form['password'] = 'test'
        else:
            form['password'] = 'testtest'
        
        r = form.submit()
        r = r.follow()
        r.mustcontain('You logged in successfully!')
        
        if cls.first:
            assert r.request.url == '/users/change_password'
            form = r.forms[0]
            form['old_password'] = 'test'
            form['password'] = 'testtest'
            form['confirm_password'] = 'testtest'
        else:
            assert r.request.url == '/control-panel'
        
        cls.first = False


