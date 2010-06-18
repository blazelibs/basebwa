from pysmvt import ag, rg, settings, user
from pysmvt.views import View, SecureView

from appstack.utils import control_panel_permission_filter
import forms

class SystemError(View):
    def default(self):
        self.status_code = 500
        self.render_template()

class AuthError(View):
    def default(self):
        self.status_code = 401
        self.render_template()

class Forbidden(View):
    def default(self):
        self.status_code = 403
        self.render_template()

class BadRequestError(View):
    def default(self):
        self.status_code = 400
        self.render_template()

class NotFoundError(View):
    def default(self):
        self.status_code = 404
        self.render_template('not_found.html')

class BlankPage(View):
    """ not truly blank, wrapped in the default layout """
    def default(self):
        self.render_template()

class DynamicControlPanel(SecureView):
    def init(self):
        self.require_all = 'webapp-controlpanel'

    def default(self):
        sections = []
        for plugin in settings.plugins:
            try:
                if plugin.cp_nav.enabled:
                    sections.append(plugin.cp_nav.section)
            except AttributeError:
                pass

        def seccmp(first, second):
            return cmp(first.heading.lower(), second.heading.lower())
        sections.sort(seccmp)
        sections = control_panel_permission_filter(user, *sections)
        self.assign('sections', sections)
        self.render_template()

class HomePage(View):
    def default(self):
        self.render_template()

class TestForm(SecureView):
    def prep(self):
        self.require_all = 'webapp-controlpanel'

    def auth_post(self, is_static=False):
        self.form = forms.TestForm(is_static)

    def post(self):
        if self.form.is_cancel():
            user.add_message('notice', 'form submission cancelled, data not changed')
            self.default()
        if self.form.is_valid():
            try:
                user.add_message('notice', 'form posted succesfully')
                self.assign('result', self.form.get_values())
                return
            except Exception, e:
                # if the form can't handle the exception, re-raise it
                if not self.form.handle_exception(e):
                    raise
        elif not self.form.is_submitted():
            # form was not submitted, nothing left to do
            return

        # form was either invalid or caught an exception, assign error
        # messages
        self.form.assign_user_errors()
        self.default()

    def default(self):
        self.assign('form', self.form)
        self.render_template()
