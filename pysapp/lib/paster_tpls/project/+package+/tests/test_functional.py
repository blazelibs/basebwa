from pysmvt import ag
from pysmvt.test import Client
from werkzeug import BaseResponse

testapp = ag._wsgi_test_app

def test_index():
    c = Client(testapp, BaseResponse)
    r = c.get('/')
    assert r.status_code == 200, r.status

def test_static():
    c = Client(testapp, BaseResponse)
    r = c.get('/c/default.css')
    assert r.status_code == 200, r.status