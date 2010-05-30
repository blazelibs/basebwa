from pysmvt import ag
from pysmvt.test import Client
from werkzeug import BaseResponse

testapp = ag._wsgi_test_app

def test_default():
    c = Client(testapp, BaseResponse)
    r = c.get('/')
    assert r.status_code == 200, r.status
    assert 'Default Module\'s Index Page' in r.data