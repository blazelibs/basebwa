from blazeweb.users import User
from basebwa.lib.cpanel import ControlPanelGroup, ControlPanelSection, \
    ControlPanelLink, control_panel_permission_filter

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
        filtered = control_panel_permission_filter(user, users_cpsec, foo_cpsec )
        assert not filtered

        user = self._setup_session_user('users-manage')
        filtered = control_panel_permission_filter(user, users_cpsec, foo_cpsec )
        assert len(filtered) == 1
        assert filtered[0]['sec'] is users_cpsec
        assert filtered[0]['sec_groups'][0]['group'] is users_cpsec.groups[0]
        assert filtered[0]['sec_groups'][0]['group_links'][0] is users_cpsec.groups[0].links[0]
        assert filtered[0]['sec_groups'][0]['group_links'][1] is users_cpsec.groups[0].links[1]
        assert filtered[0]['sec_groups'][1]['group'] is users_cpsec.groups[1]
        assert filtered[0]['sec_groups'][1]['group_links'][0] is users_cpsec.groups[1].links[0]
        assert len(filtered[0]['sec_groups'][1]['group_links']) == 1

        user = self._setup_session_user('foo-manage')
        filtered = control_panel_permission_filter(user, users_cpsec, foo_cpsec )
        assert len(filtered) == 1
        assert filtered[0]['sec'] is foo_cpsec
        assert filtered[0]['sec_groups'][0]['group'] is foo_cpsec.groups[1]
        assert len(filtered[0]['sec_groups']) == 1
        assert filtered[0]['sec_groups'][0]['group_links'][0] is foo_cpsec.groups[1].links[0]
        assert len(filtered[0]['sec_groups'][0]['group_links']) == 1
