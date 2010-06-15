# -*- coding: utf-8 -*-

from pysmvt import ag, rg, appimportauto, settings, user
import forms
appimportauto('base', ['PublicSnippetView', 'PublicPageView', 'ProtectedPageView'])
appimportauto('utils', 'control_panel_permission_filter')

class UserMessagesSnippet(PublicSnippetView):
    
    def default(self, heading = 'System Message(s)'):        
        self.assign('heading', heading)

class SystemError(PublicPageView):
    
    def default(self):
        if not rg.environ.has_key('pysmvt.controller.error_docs_handler.response'):
            # internal server error
            self.response.status_code = 500

class AuthError(PublicPageView):
    
    def default(self):
        if not rg.environ.has_key('pysmvt.controller.error_docs_handler.response'):
            # unauthorized
            self.response.status_code = 401

class Forbidden(PublicPageView):
    
    def default(self):
        if not rg.environ.has_key('pysmvt.controller.error_docs_handler.response'):
            # forbidden
            self.response.status_code = 403

class BadRequestError(PublicPageView):
    
    def default(self):
        if not rg.environ.has_key('pysmvt.controller.error_docs_handler.response'):
            # Bad Request
            self.response.status_code = 400

class NotFoundError(PublicPageView):
    
    def default(self):
        if not rg.environ.has_key('pysmvt.controller.error_docs_handler.response'):
            # Bad Request
            self.response.status_code = 404


class BlankPage(PublicPageView):
    
    def default(self):
        pass
    
class ControlPanel(ProtectedPageView):
    def prep(self):
        self.require = 'webapp-controlpanel'
        
    def default(self):
        pass
    
class DynamicControlPanel(ProtectedPageView):
    def prep(self):
        self.require = 'webapp-controlpanel'
        
    def default(self):
        sections = []
        for mod in settings.modules:
            try:
                if mod.cp_nav.enabled:
                    sections.append(mod.cp_nav.section)
            except AttributeError:
                pass

        def seccmp(first, second):
            return cmp(first.heading.lower(), second.heading.lower())
        sections.sort(seccmp)
        sections = control_panel_permission_filter(user, *sections)
        self.assign('sections', sections)

class HomePage(PublicPageView):
    def default(self):
        pass

class TestForm(ProtectedPageView):
    def prep(self):
        self.require = 'webapp-controlpanel'
        
    def post_auth_setup(self, is_static=False):
        self.form = forms.TestForm(is_static)
    
    def post(self, is_static=False):
        if self.form.is_cancel():
            user.add_message('notice', 'form submission cancelled, data not changed')
            self.default(is_static)
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
        self.default(is_static)
        
    def default(self, is_static=False):
        self.assign('form', self.form)