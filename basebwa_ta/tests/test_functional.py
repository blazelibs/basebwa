from blazeweb.globals import ag, settings
from blazeweb.testing import TestApp
from nose.tools import eq_

from authbwc.lib.testing import login_client_with_permissions
from commonbwc.lib.testing import has_message
from compstack.sqlalchemy import db
from basebwa_ta.model.orm import Widget

class TestCrud(object):
    @classmethod
    def setup_class(cls):
        cls.ta = TestApp(ag.wsgi_test_app)

    def create_widget(self, widget_type, color, quantity):
        w = Widget(widget_type=widget_type, color=color, quantity=quantity)
        db.sess.add(w)
        db.sess.commit()
        return w

    def test_add(self):
        r = self.ta.get('/widget/add/999999', status=400)

        r = self.ta.get('/widget/add')
        d = r.pyq
        eq_(d('form:first').attr('id'), 'widget-form', r)
        assert d('h2').text() == 'Add Widget'
        assert d('form#widget-form').attr.action == '/widget/add'
        assert d('span#widget-form-cancel a').attr.href == '/widget/manage'

        r.form['widget_type'] = 'Type A'
        r.form['color'] = 'silver'
        r = r.form.submit('submit', status=200)
        assert '/widget/add' in r.request.url

        r.form['quantity'] = '87'
        r = r.form.submit('submit', status=302)
        assert '/widget/add' in r.request.url
        r = r.follow(status=200)
        assert '/widget/manage' in r.request.url

    def test_edit(self):
        r = self.ta.get('/widget/edit', status=404)
        r = self.ta.get('/widget/edit/999999', status=404)

        w_id = self.create_widget(u'edit_test_widget', u'black', 150).id
        r = self.ta.get('/widget/edit/%s'%w_id)
        d = r.pyq
        eq_(d('form:first').attr('id'), 'widget-form', r)
        assert d('form#widget-form').attr.action == '/widget/edit/%s'%w_id
        assert d('h2').text() == 'Edit Widget'
        assert d('input[name="widget_type"]').val() == 'edit_test_widget'
        assert d('input[name="color"]').val() == 'black'
        assert d('input[name="quantity"]').val() == '150'

        r.form['quantity'] = '75'
        r = r.form.submit('submit', status=302)
        assert '/widget/edit/%s'%w_id in r.request.url
        r = r.follow(status=200)
        assert '/widget/manage' in r.request.url

        w = Widget.get(w_id)
        assert w.quantity == 75

    def test_manage(self):
        r = self.ta.get('/widget/manage/999999', status=400)
        r = self.ta.post('/widget/manage', status=400)

        w_id = self.create_widget(u'manage_test_widget', u'black', 150).id

        r = self.ta.get('/widget/manage?filteron=type&filteronop=eq&filterfor=manage_test_widget')
        d = r.pyq
        assert d('form#widget-form').html() is None
        assert d('h2:eq(0)').text() == 'Manage Widgets'
        assert d('p a').eq(0).attr.href == '/widget/add'
        assert d('a[href="/widget/edit/%s"]'%w_id).html() is not None
        assert d('a[href="/widget/delete/%s"]'%w_id).html() is not None

    def test_delete(self):
        r = self.ta.get('/widget/delete', status=404)
        r = self.ta.get('/widget/delete/999999', status=404)

        w_id = self.create_widget(u'delete_test_widget', u'black', 150).id
        r = self.ta.post('/widget/delete/%s'%w_id, status=400)
        r = self.ta.get('/widget/delete/%s'%w_id, status=302)
        assert '/widget/delete/%s'%w_id in r.request.url

        r = r.follow(status=200)
        assert '/widget/manage' in r.request.url

        w = Widget.get(w_id)
        assert w is None

    def test_bad_action(self):
        r = self.ta.get('/widget/badaction', status=404)
        r = self.ta.get('/widget/badaction/999999', status=404)

    def test_delete_protect(self):
        w_id = self.create_widget(u'delete_protect_test_widget', u'black', 150).id

        r = self.ta.get('/widget-auth/manage?filteron=type&filteronop=eq&filterfor=delete_protect_test_widget')
        d = r.pyq
        assert d('a[href="/widget-auth/edit/%s"]'%w_id).html() is not None
        assert d('a[href="/widget-auth/delete/%s"]'%w_id).html() is None
        r = self.ta.get('/widget-auth/delete/%s'%w_id, status=403)

        login_client_with_permissions(self.ta, u'widget-delete')
        r = self.ta.get('/widget-auth/manage?filteron=type&filteronop=eq&filterfor=delete_protect_test_widget')
        d = r.pyq
        assert d('a[href="/widget-auth/edit/%s"]'%w_id).html() is not None
        assert d('a[href="/widget-auth/delete/%s"]'%w_id).html() is not None
        r = self.ta.get('/widget-auth/delete/%s'%w_id, status=302)
        self.ta.get('/users/logout')

class TestFormErrors(object):
    @classmethod
    def setup_class(cls):
        cls.ta = TestApp(ag.wsgi_test_app)

    def test_required(self):
        r = self.ta.get('/widget/add')
        r.form['widget_type'] = 'Type A'
        r.form['color'] = 'silver'
        r = r.form.submit('submit', status=200)
        d = r.pyq
        assert has_message(d, 'error', 'Quantity: field is required')

    def test_maxlength(self):
        r = self.ta.get('/widget/add')
        r.form['widget_type'] = ''.join(['a' for i in range(260)])
        r.form['color'] = 'silver'
        r.form['quantity'] = 125
        r = r.form.submit('submit', status=200)
        d = r.pyq
        assert has_message(d, 'error', 'Type: Enter a value not greater than 255 characters long')

class TestAdminTemplating(object):

    @classmethod
    def setup_class(cls):
        cls.ta = TestApp(ag.wsgi_test_app)
        settings.template.admin = 'admin.html'

    def test_primary_content_block(self):
        r = self.ta.get('/admin-templating/pc-block')
        assert 'pc content' in r

class TestDefaultTemplating(TestAdminTemplating):

    @classmethod
    def setup_class(cls):
        cls.ta = TestApp(ag.wsgi_test_app)
        settings.template.admin = 'default.html'
