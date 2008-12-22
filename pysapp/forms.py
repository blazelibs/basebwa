# -*- coding: utf-8 -*-
from pyhtmlquickform.form import Form as QForm
from pysmvt import rg, user
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
        # don't want to repeat the assignment and is_submitted might be used
        # more than once
        if not self._request_submitted:
            tosubmit = rg.request.form.copy()
            tosubmit.update(rg.request.files)
            self.set_submitted(tosubmit)
            self._request_submitted = True
        return Pysform.is_submitted(self)
    
    def assign_user_errors(self):
        # set the form error messages first
        for msg in self.errors:
            user.add_message('error', msg)
        # set element error messages
        for el in self.submittable_els.values():
            for msg in el.errors:
                user.add_message('error', '%s: %s' % (el.label, msg))