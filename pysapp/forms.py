# -*- coding: utf-8 -*-
from pyhtmlquickform.form import Form as QForm
from pysmvt import rg
from pysform.form import Form as Pysform

class QuickFormBase(QForm):

    def __init__(self, name, **kwargs):
        QForm.__init__(self, name, class_='generated', **kwargs)
        self._request_submitted = False
        
    def isSubmitted(self, submitValues = None):
        # don't want to repeat this and isSubmitted can be used
        # more than once
        if not self._request_submitted:
            self.set_submitted(rg.request.form)
            self.set_files(rg.request.files)
            self._request_submitted = True
        return QForm.isSubmitted(self, submitValues)

class Form(Pysform):
    def __init__(self, name, **kwargs):
        Pysform.__init__(self, name, class_='generated', **kwargs)
        self._request_submitted = False
        
    def is_submitted(self):
        # don't want to repeat the assignment and is_submitted can be used
        # more than once
        if not self._request_submitted:
            self.set_submitted(rg.request.form)
            self.set_files(rg.request.files)
            self._request_submitted = True
        return Pysform.is_submitted(self)