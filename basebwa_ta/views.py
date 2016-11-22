from blazeweb.globals import user
from blazeweb.views import View, asview
from commonbwc.lib.views import CrudBase, FormMixin

import basebwa_ta.forms as forms
import basebwa_ta.grids as grids
import basebwa_ta.model.orm as orm


class FormTest1(View, FormMixin):
    def setup_view(self):
        self.form_init(forms.NameForm)

    def form_assign_defaults(self):
        self.form.els.email.defaultval = 'foo@example.com'

    def form_on_valid(self):
        if not self.form.els.email.value:
            raise ValueError('email is empty')
        return 'Hello %s' % self.form.els.name.value

    def form_on_cancel(self):
        return 'cancelled'

    def form_on_invalid(self):
        return 'invalid'


class FormTest2(View, FormMixin):
    def setup_view(self, cancel_type=None):
        self.form_init(forms.NameForm)
        if cancel_type == 'url':
            self.cancel_url = '/somewhere'
        elif cancel_type == 'endpoint':
            self.cancel_endpoint = 'FormTest1'

    def form_on_valid(self):
        if not self.form.els.email.value:
            raise ValueError('email is empty')
        user.add_message('notice', 'Hello %s' % self.form.els.name.value)


class WidgetCrud(CrudBase):

    def init(self):
        CrudBase.init(self, 'Widget', 'Widgets', forms.WidgetForm, orm.Widget,
                      grids.WidgetGrid)
        self.allow_anonymous = True


class WidgetCrudDeletePerm(WidgetCrud):

    def init(self):
        WidgetCrud.init(self)
        self.gridcls = grids.WidgetAuthGrid
        self.delete_protect = True
        self.delete_require_any = 'widget-delete'


@asview('/')
def home_page():
    return user.get_messages()
