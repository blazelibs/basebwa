from pysmvt import modimportauto, modimport, settings, ag
from pysmvt.test import Client
from pysmvt.utils import randchars
from werkzeug import BaseResponse

testapp = ag._wsgi_test_app

modimportauto('users.testing', ['login_client_with_permissions'])

class TestDynamicControlPanel(object):

    @classmethod
    def setup_class(cls):
        permission_add = modimport('users.actions', 'permission_add')
        
        cls.c = Client(testapp, BaseResponse)
        login_client_with_permissions(cls.c, (u'webapp-controlpanel', u'users-manage'))

    def test_panel(self):
        r = self.c.get('/control-panel')
        assert r.status == '200 OK'
        expected = ''.join("""
    <div class="module_wrapper">
        <h2>Users</h2>
        <ul class="link_group">
        <li><a href="/users/add">User Add</a></li>
        <li><a href="/users/manage">Users Manage</a></li>
        </ul>
        <ul class="link_group">
            <li><a href="/groups/add">Group Add</a></li>
            <li><a href="/groups/manage">Groups Manage</a></li>
        </ul>
        <ul class="link_group">
        
            <li><a href="/permissions/manage">Permissions Manage</a></li>
        </ul>
    </div>""".split())
        assert expected in ''.join(r.data.split())
        