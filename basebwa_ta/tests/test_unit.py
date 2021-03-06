from io import BytesIO
from basebwa.lib.cpanel import ControlPanelGroup, ControlPanelSection, \
    ControlPanelLink, control_panel_permission_filter
from blazeweb.testing import inrequest
from blazeweb.users import User
from blazeweb.views import View
from blazeweb.wrappers import Request

from commonbwc.lib.forms import Form as CommonForm


class TestForms(object):

    @inrequest('/')
    def test_view(self):

        class FormTest(View):
            def default(self):
                return 'foo'

        ft = FormTest({}, 'formtest')
        r = ft.process()
        assert r.data == b'foo', r.data

    @classmethod
    def setup_class(cls):
        class TestForm(CommonForm):
            def init(self):
                self.add_text('name_first', 'First name', maxlength=30)
                self.add_file('txtfile', 'Text File')
        cls.Form = TestForm

    def test_with_no_request_object(self):
        f = self.Form()
        assert not f.is_submitted()

    @inrequest()
    def test_auto_form_submit(self):
        # setup the request, which will bind to the app's rg.request
        # which should result in the form values getting submitted
        Request.from_values(
            {
                'name_first': 'bob',
                'txtfile': (BytesIO(b'my file contents'), 'test.txt'),
                'test-form-submit-flag': 'submitted'
            },
            bind_to_context=True
        )
        # test the form
        f = self.Form()
        assert f.is_submitted()
        assert f.is_valid()
        assert f.name_first.value == 'bob'
        assert f.txtfile.value.file_name == 'test.txt'
        assert f.txtfile.value.content_type == 'text/plain'


class TestControlPanelFilter(object):

    def _setup_session_user(self, *perms):
        user = User()

        # now permissions
        for perm in perms:
            user.add_perm(perm)
        return user

    def test_no_perms(self):
        users_cpsec = ControlPanelSection(
            "Users",
            'users-manage',
            ControlPanelGroup(
                ControlPanelLink('User Add', 'users:UserUpdate'),
                ControlPanelLink('Users Manage', 'users:UserManage'),
            ),
            ControlPanelGroup(
                ControlPanelLink('A', 'e:a'),
                ControlPanelLink('B', 'e:b', has_perm='access-b'),
            ),
        )
        foo_cpsec = ControlPanelSection(
            "Foo",
            'foo-manage',
            ControlPanelGroup(
                ControlPanelLink('Foo Add', 'foo:FooUpdate'),
                ControlPanelLink('Foo Manage', 'foo:FooManage'),
                has_perm='foo-group'
            ),
            ControlPanelGroup(
                ControlPanelLink('A', 'e:a'),
            )
        )
        user = self._setup_session_user()
        filtered = control_panel_permission_filter(user, users_cpsec, foo_cpsec)
        assert not filtered

        user = self._setup_session_user('users-manage')
        filtered = control_panel_permission_filter(user, users_cpsec, foo_cpsec)
        assert len(filtered) == 1
        assert filtered[0]['sec'] is users_cpsec
        assert filtered[0]['sec_groups'][0]['group'] is users_cpsec.groups[0]
        assert filtered[0]['sec_groups'][0]['group_links'][0] is users_cpsec.groups[0].links[0]
        assert filtered[0]['sec_groups'][0]['group_links'][1] is users_cpsec.groups[0].links[1]
        assert filtered[0]['sec_groups'][1]['group'] is users_cpsec.groups[1]
        assert filtered[0]['sec_groups'][1]['group_links'][0] is users_cpsec.groups[1].links[0]
        assert len(filtered[0]['sec_groups'][1]['group_links']) == 1

        user = self._setup_session_user('foo-manage')
        filtered = control_panel_permission_filter(user, users_cpsec, foo_cpsec)
        assert len(filtered) == 1
        assert filtered[0]['sec'] is foo_cpsec
        assert filtered[0]['sec_groups'][0]['group'] is foo_cpsec.groups[1]
        assert len(filtered[0]['sec_groups']) == 1
        assert filtered[0]['sec_groups'][0]['group_links'][0] is foo_cpsec.groups[1].links[0]
        assert len(filtered[0]['sec_groups'][0]['group_links']) == 1
