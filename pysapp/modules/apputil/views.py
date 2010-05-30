# -*- coding: utf-8 -*-

from pysmvt import ag, rg, appimportauto, settings
appimportauto('base', ['PublicSnippetView', 'PublicPageView', 'ProtectedPageView'])

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
        self.assign('sections', sections)
        