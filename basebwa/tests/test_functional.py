from blazeweb.globals import ag
from webtest import TestApp

ta = TestApp(ag.wsgi_test_app)

def test_index():
    r = ta.get('/')
    r.mustcontain('Not a lot here')
