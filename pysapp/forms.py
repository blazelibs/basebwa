# -*- coding: utf-8 -*-
from pyhtmlquickform.form import Form
from pysmvt import rg

class QuickFormBase(Form):

    def __init__(self, name, **kwargs):
        Form.__init__(self, name, class_='generated', **kwargs)
        self._request_submitted = False
        
    def isSubmitted(self, submitValues = None):
        # don't want to repeat this and isSubmitted can be used
        # more than once
        if not self._request_submitted:
            self.set_submitted(rg.request.form)
            self.set_files(rg.request.files)
            self._request_submitted = True
        return Form.isSubmitted(self, submitValues)