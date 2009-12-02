from pysmvt import modimportauto, modimport, settings, ag
from pysmvt.test import Client
from pysmvt.utils import randchars
from werkzeug import BaseResponse

testapp = ag._wsgi_test_app

modimportauto('users.testing', ['login_client_with_permissions'])

class TestDynamicControlPanel(object):

    @classmethod
    def setup_class(cls):
        cls.link_permission_name = randchars(32)
        permission_add = modimport('users.actions', 'permission_add')
        permission_add(name=unicode(cls.link_permission_name), safe='unique')
        settings.unlock()
        settings.modules.apputil.cp_nav.enabled = True
        
        cls.c = Client(testapp, BaseResponse)
        login_client_with_permissions(cls.c, (u'webapp-controlpanel'))

    @classmethod
    def teardown_class(cls):
        permission_delete = modimport('users.actions', 'permission_delete')
        permission_get_by_name = modimport('users.actions', 'permission_get_by_name')
        p = permission_get_by_name(cls.link_permission_name)
        permission_delete(p.id)
        settings.modules.apputil.cp_nav.enabled = False
        settings.lock()

    def test_panel(self):
        r = self.c.get('/control-panel')
        assert r.status == '200 OK'