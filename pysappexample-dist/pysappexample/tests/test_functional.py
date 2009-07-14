from pysmvt import appimportauto, ag
from werkzeug import Client, BaseResponse

testapp = ag._wsgi_test_app

def test_index():
    c = Client(testapp, BaseResponse)
    r = c.get('/')
    assert r.status_code == 200, r.status

