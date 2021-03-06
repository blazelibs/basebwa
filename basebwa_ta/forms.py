from basebwa.lib.forms import Form
from blazeweb.routing import url_for
from webhelpers2.html.tags import link_to


class NameForm(Form):
    def init(self):
        self.add_text('name', 'Name', required=True)
        el = self.add_text('email', 'Email')
        el.add_handler('email is empty')
        self.add_submit('submit')
        self.add_cancel('cancel')


class WidgetForm(Form):
    def init(self):
        self.add_text('widget_type', 'Type', required=True)
        self.add_text('color', 'Color', required=True)
        self.add_text('quantity', 'Quantity', required=True)

        sg = self.add_elgroup('submit-group', class_='submit-only')
        sg.add_submit('submit')
        cancel_url = link_to('Cancel', url_for('WidgetCrud', action='manage'),
                             title='Go back to the manage page')
        sg.add_static('cancel', None, cancel_url)
