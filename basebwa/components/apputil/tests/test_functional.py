from blazeutils.strings import randchars
from werkzeug import BaseResponse
from blazeweb.globals import settings, ag
from blazeweb.testing import Client

from compstack.auth.lib.testing import login_client_with_permissions

testapp = ag.wsgi_test_app

class TestDynamicControlPanel(object):

    @classmethod
    def setup_class(cls):

        cls.c = Client(testapp, BaseResponse)
        login_client_with_permissions(cls.c, (u'webapp-controlpanel', u'auth-manage'))

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
