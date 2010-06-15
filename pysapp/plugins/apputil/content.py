from pysmvt import ag, rg, settings, user

from appstack.utils import control_panel_permission_filter
import forms

class UserMessagesSnippet(PublicSnippetView):

    def create(self, heading = 'System Message(s)'):
        self.assign('heading', heading)
