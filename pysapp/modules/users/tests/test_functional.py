import datetime
from pysmvt import modimportauto, ag, db
from werkzeug import Client, BaseResponse, BaseRequest

modimportauto('users.testing', ['login_client_with_permissions',
    'login_client_as_user', 'create_user_with_permissions'])
modimportauto('users.actions', ['user_get', 'permission_get_by_name',
    'user_get_by_email', 'group_add', 'user_permission_map',
    'user_assigned_perm_ids', 'user_group_ids'])
            
class TestUserViews(object):

    @classmethod
    def setup_class(cls):
        cls.c = Client(ag._wsgi_test_app, BaseResponse)
        perms = [u'users-manage', u'users-test1', u'users-test2']
        cls.userid = login_client_with_permissions(cls.c, perms)
        
    def test_required_fields(self):
        topost = {
          'user-form-submit-flag':'submitted'
        }
        r = self.c.post('users/add', data=topost)
        assert r.status_code == 200, r.status
        assert 'Email: field is required' in r.data
        assert 'Login Id: field is required' in r.data
        
    def test_loginid_unique(self):
        user = user_get(self.userid)
        topost = {
            'login_id': user.login_id,
            'password': 'testtest',
            'email_address': 'test@example.com',
            'password-confirm': 'testtest',
            'email': 'test@exacmple.com',
            'user-form-submit-flag':'submitted',
            'inactive_flag': False,
            'inactive_date': '',
            'name_first': '',
            'name_last': ''
        }
        r = self.c.post('users/add', data=topost)
        assert r.status_code == 200, r.status
        assert 'Login Id: That user already exists' in r.data
        
    def test_loginid_maxlength(self):
        topost = {
            'login_id': 'r'*151,
            'user-form-submit-flag':'submitted'
        }
        r = self.c.post('users/add', data=topost)
        assert 'Login Id: Enter a value less than 150 characters long' in r.data
    
    def test_email_unique(self):
        user = user_get(self.userid)
        topost = {
            'login_id': 'newuser',
            'password': 'testtest',
            'email_address': user.email_address,
            'password-confirm': 'testtest',
            'email': 'test@exacmple.com',
            'user-form-submit-flag':'submitted',
            'inactive_flag': False,
            'inactive_date': '',
            'name_first': '',
            'name_last': ''
        }
        r = self.c.post('users/add', data=topost)
        assert r.status_code == 200, r.status
        assert 'Email: A user with that email address already exists' in r.data
    
    def test_email_maxlength(self):
        topost = {
            'email_address': 'r'*151,
            'user-form-submit-flag':'submitted'
        }
        r = self.c.post('users/add', data=topost)
        assert r.status_code == 200, r.status
        assert 'Email: Enter a value less than 150 characters long' in r.data
    
    def test_email_format(self):
        topost = {
            'email_address': 'test',
            'user-form-submit-flag':'submitted'
        }
        r = self.c.post('users/add', data=topost)
        assert r.status_code == 200, r.status
        assert 'Email: An email address must contain a single @' in r.data
        
    def test_bad_confirm(self):
        topost = {
            'login_id': 'newuser',
            'password': 'testtest',
            'email_address': 'abc@example.com',
            'password-confirm': 'nottests',
            'email': 'test@exacmple.com',
            'user-form-submit-flag':'submitted'
        }
        r = self.c.post('users/add', data=topost)
        assert r.status_code == 200, r.status
        assert 'Confirm Password: does not match field "Password"' in r.data
    
    def test_super_user_protection(self):
        r = self.c.get('users/add')
        assert 'name="super_user"' not in r.data
    
    def test_perms_legit(self):
        p = permission_get_by_name(u'users-test1')
        perm = [str(p.id)]
        topost = {
            'login_id': 'newuser',
            'password': 'testtest',
            'email_address': 'abc@example.com',
            'password-confirm': 'testtest',
            'email': 'test@exacmple.com',
            'user-form-submit-flag':'submitted',
            'approved_permissions': perm,
            'denied_permissions': perm
        }
        r = self.c.post('users/add', data=topost)
        assert r.status_code == 200, r.status
        assert 'Denied: you can not approve and deny the same permission' in r.data
        assert 'Approved: you can not approve and deny the same permission' in r.data
    
    def test_fields_saved(self):
        ap = permission_get_by_name(u'users-test1').id
        dp = permission_get_by_name(u'users-test2').id
        gp = group_add(name=u'test-group', approved_permissions=[],
                      denied_permissions=[], assigned_users=[], safe='unique').id
        topost = {
            'login_id': 'usersaved',
            'email_address': 'usersaved@example.com',
            'user-form-submit-flag':'submitted',
            'approved_permissions': ap,
            'denied_permissions': dp,
            'assigned_groups': gp,
            'super_user': 1,
            'inactive_flag': False,
            'inactive_date': '10/11/2010',
            'name_first': 'test',
            'name_last': 'user'
        }
        r = self.c.post('users/add', data=topost, follow_redirects=True)
        assert r.status_code == 200, r.status
        assert 'user added' in r.data
        
        user = user_get_by_email(u'usersaved@example.com')
        assert user.login_id == 'usersaved'
        assert user.reset_required
        assert not user.super_user
        assert user.pass_hash
        assert user.groups[0].name == 'test-group'
        assert len(user.groups) == 1
        assert user.inactive_date == datetime.datetime(2010, 10, 11), user.inactive_date
        assert user.name_first == 'test'
        assert user.name_last == 'user'
        
        found = 3
        for permrow in user_permission_map(user.id):
            if permrow['permission_name'] == u'users-test1':
                assert permrow['resulting_approval']
                found -= 1
            if permrow['permission_name'] in (u'users-test2', u'users-manage'):
                assert not permrow['resulting_approval']
                found -= 1
        assert found == 0
        
        # now test an edit
        topost = {
            'login_id': 'usersaved',
            'email_address': 'usersaved@example.com',
            'user-form-submit-flag':'submitted',
            'approved_permissions': dp,
            'denied_permissions': ap,
            'assigned_groups': None,
            'super_user': 1,
            'inactive_flag': False,
            'inactive_date': '10/10/2010',
            'name_first': 'test2',
            'name_last': 'user2'
        }
        r = self.c.post('users/edit/%s' % user.id, data=topost, follow_redirects=True)
        assert 'user edited successfully' in r.data
        
        user = user_get_by_email(u'usersaved@example.com')
        assert user.login_id == 'usersaved'
        assert not user.reset_required
        assert not user.super_user
        assert user.pass_hash
        assert len(user.groups) == 0
        assert user.inactive_date == datetime.datetime(2010, 10, 10), user.inactive_date
        assert user.name_first == 'test2'
        assert user.name_last == 'user2'
        
        found = 3
        for permrow in user_permission_map(user.id):
            if permrow['permission_name'] == u'users-test2':
                assert permrow['resulting_approval']
                found -= 1
            if permrow['permission_name'] in (u'users-test1', u'users-manage'):
                assert not permrow['resulting_approval']
                found -= 1
        assert found == 0
        
        # test edit w/ reset required
        topost = {
            'login_id': 'usersaved',
            'email_address': 'usersaved@example.com',
            'user-form-submit-flag':'submitted',
            'approved_permissions': dp,
            'denied_permissions': ap,
            'assigned_groups': None,
            'super_user': 1,
            'reset_required': 1,
            'inactive_flag': False,
            'inactive_date': '',
            'name_first': '',
            'name_last': ''
        }
        r = self.c.post('users/edit/%s' % user.id, data=topost, follow_redirects=True)
        assert 'user edited successfully' in r.data
        
        user = user_get_by_email(u'usersaved@example.com')
        assert user.login_id == 'usersaved'
        assert user.reset_required
        assert not user.super_user
        assert user.pass_hash
        assert len(user.groups) == 0
        
        # now test a delete
        r = self.c.get('users/delete/%s' % user.id, follow_redirects=True)
        assert r.status_code == 200, r.status
        assert 'user deleted' in r.data
    
    def test_password_complexity(self):
        topost = {
            'login_id': 'newuser',
            'password': 't',
            'email_address': 'abc@example.com',
            'password-confirm': 't',
            'email': 'test@exacmple.com',
            'user-form-submit-flag':'submitted'
        }
        r = self.c.post('users/add', data=topost)
        assert r.status_code == 200, r.status
        assert 'Password: Enter a value at least 6 characters long' in r.data
        
        topost = {
            'login_id': 'newuser',
            'password': 't'*26,
            'email_address': 'abc@example.com',
            'password-confirm': 't'*26,
            'email': 'test@exacmple.com',
            'user-form-submit-flag':'submitted'
        }
        r = self.c.post('users/add', data=topost)
        assert r.status_code == 200, r.status
        assert 'Password: Enter a value less than 25 characters long' in r.data

    def test_same_user_delete(self):
        r = self.c.get('users/delete/%s' % self.userid, follow_redirects=True)
        assert r.status_code == 200, r.status
        assert 'You cannot delete your own user account' in r.data


class TestUserProfileView(object):

    @classmethod
    def setup_class(cls):
        cls.c = Client(ag._wsgi_test_app, BaseResponse)
        cls.userid = login_client_with_permissions(cls.c, u'prof-test-1', u'prof-test-2')
        cls.userid2 = create_user_with_permissions().id
        
    def get_to_post(self):
        user = user_get(self.userid)
        topost = {
            'name_first': 'usersfirstname',
            'name_last': 'userslastname',
            'login_id': user.login_id,
            'email_address': user.email_address,
            'user-profile-form-submit-flag':'submitted'
        }
        return topost

    def test_fields_load(self):
        """ make sure fields load with data currently in db """
        r = self.c.get('users/profile')
        assert r.status_code == 200, r.status
        user = user_get(self.userid)
        assert user.email_address in r.data
        assert user.login_id in r.data
        
        r = self.c.post('users/profile', data=self.get_to_post())
        assert r.status_code == 200, r.status
        user = user_get(self.userid)
        assert user.email_address in r.data
        assert user.login_id in r.data
        assert 'usersfirstname' in r.data
        assert 'userslastname' in r.data
        assert 'profile updated succesfully' in r.data
        
    def test_required_fields(self):
        topost = self.get_to_post()
        topost['email_address'] = None
        r = self.c.post('users/profile', data=topost)
        assert r.status_code == 200, r.status
        assert 'Email: field is required' in r.data
        
        topost = self.get_to_post()
        topost['login_id'] = None
        r = self.c.post('users/profile', data=topost)
        assert r.status_code == 200, r.status
        assert 'Login Id: field is required' in r.data
    
    def test_password_confirm(self):
        topost = self.get_to_post()
        topost['password'] = 'newpass'
        topost['password-confirm'] = 'nomatch'
        r = self.c.post('users/profile', data=topost)
        assert r.status_code == 200, r.status
        assert 'Confirm Password: does not match field "Password"' in r.data

    def test_email_dups(self):
        user2 = user_get(self.userid2)
        topost = self.get_to_post()
        topost['email_address'] = user2.email_address
        r = self.c.post('users/profile', data=topost)
        assert r.status_code == 200, r.status
        assert 'Email: A user with that email address already exists' in r.data
        
    def test_login_id_dups(self):
        user2 = user_get(self.userid2)
        topost = self.get_to_post()
        topost['login_id'] = user2.login_id
        r = self.c.post('users/profile', data=topost)
        assert r.status_code == 200, r.status
        assert 'Login Id: That user already exists.' in r.data
    
    def test_cancel(self):
        topost = self.get_to_post()
        topost['cancel'] = 'submitted'
        r = self.c.post('users/profile', data=topost, follow_redirects=True)
        assert r.status_code == 200, r.status
        assert 'no changes made to your profile' in r.data
    
    def test_password_changes(self):
        user = user_get(self.userid)
        pass_hash = user.pass_hash
        
        r = self.c.post('users/profile', data=self.get_to_post())
        assert r.status_code == 200, r.status
        user = user_get(self.userid)
        assert user.pass_hash == pass_hash
        
        topost = self.get_to_post()
        topost['password'] = 'newpass'
        topost['password-confirm'] = 'newpass'
        r = self.c.post('users/profile', data=topost)
        assert r.status_code == 200, r.status
        user = user_get(self.userid)
        assert user.pass_hash != pass_hash
        
    def test_perm_changes(self):
        p1 = permission_get_by_name(u'prof-test-1').id
        p2 = permission_get_by_name(u'prof-test-2').id
        
        # add user to group
        user = user_get(self.userid)
        gp = group_add(name=u'test-group', approved_permissions=[],
                      denied_permissions=[], assigned_users=[user.id], safe='unique').id
        
        r = self.c.post('users/profile', data=self.get_to_post())
        assert r.status_code == 200, r.status
        user = user_get(self.userid)
        approved, denied =  user_assigned_perm_ids(user)
        assert p1 in approved
        assert p2 in denied
        assert gp in user_group_ids(user)
    
class TestUserViewsSuperUser(object):

    @classmethod
    def setup_class(cls):
        cls.c = Client(ag._wsgi_test_app, BaseResponse)
        perms = [u'users-manage', u'users-test1', u'users-test2']
        cls.userid = login_client_with_permissions(cls.c, perms, super_user=True)
    
    def test_super_user_protection(self):
        r = self.c.get('users/add')
        assert 'name="super_user"' in r.data
        
    def test_fields_saved(self):
        ap = permission_get_by_name(u'users-test1').id
        dp = permission_get_by_name(u'users-test2').id
        gp = group_add(name=u'test-group', approved_permissions=[],
                      denied_permissions=[], assigned_users=[], safe='unique').id
        topost = {
            'login_id': 'usersavedsu',
            'password': 'testtest',
            'email_address': 'usersavedsu@example.com',
            'password-confirm': 'testtest',
            'email': 'test@exacmple.com',
            'user-form-submit-flag':'submitted',
            'approved_permissions': ap,
            'denied_permissions': dp,
            'assigned_groups': gp,
            'super_user': 1,
            'inactive_flag': False,
            'inactive_date': '',
            'name_first': '',
            'name_last': ''
        }
        r = self.c.post('users/add', data=topost, follow_redirects=True)
        assert r.status_code == 200, r.status
        assert 'user added' in r.data
        
        user = user_get_by_email(u'usersavedsu@example.com')
        assert user.login_id == 'usersavedsu'
        assert user.reset_required
        assert user.super_user
        assert user.pass_hash
        assert user.groups[0].name == 'test-group'
        assert len(user.groups) == 1
        
        found = 3
        for permrow in user_permission_map(user.id):
            if permrow['permission_name'] == u'users-test1':
                assert permrow['resulting_approval']
                found -= 1
            if permrow['permission_name'] in (u'users-test2', u'users-manage'):
                assert not permrow['resulting_approval']
                found -= 1
        assert found == 0

def test_inactive_login():
    # create a user
    user = create_user_with_permissions()
    
    # set the user's inactive flag
    user.inactive_flag = True
    db.sess.commit()
    
    # log user in
    client = Client(ag._wsgi_test_app, BaseResponse)
    req, resp = login_client_as_user(client, user.login_id, user.text_password)
    assert resp.status_code == 200, resp.status
    assert 'That user is inactive.' in resp.data
    assert req.url == 'http://localhost/users/login'