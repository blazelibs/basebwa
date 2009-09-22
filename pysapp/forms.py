# -*- coding: utf-8 -*-
from pysmvt import rg, user
from pysform.form import Form as Pysform
from pysmvt.routing import current_url
from pysform.util import NotGiven

class Form(Pysform):
    def __init__(self, name, **kwargs):
        action = kwargs.pop('action', current_url(strip_host=True))
        class_ = kwargs.pop('class_', NotGiven)
        if class_ is NotGiven:
            kwargs['class_'] = 'generated'
        elif class_:
            kwargs['class_'] = class_
        Pysform.__init__(self, name, action=action, **kwargs)
        self._request_submitted = False
        
    def is_submitted(self):
        # don't want to repeat the assignment and is_submitted might be used
        # more than once
        if not self._request_submitted:
            tosubmit = {}
            for key, value in rg.request.form.to_dict(flat=False).iteritems():
                if len(value) == 1:
                    tosubmit[key] = value[0]
                else:
                    tosubmit[key] = value
            tosubmit.update(rg.request.files.to_dict())
            self.set_submitted(tosubmit)
            self._request_submitted = True
        return Pysform.is_submitted(self)
    
    def assign_user_errors(self):
        # set the form error messages first
        for msg in self._errors:
            user.add_message('error', msg)
        # set element error messages
        for el in self._submittable_els.values():
            for msg in el.errors:
                user.add_message('error', '%s: %s' % (el.label, msg))
    
    def render(self, **kwargs):
        kwargs.setdefault('note_prefix', '- ')
        kwargs.setdefault('error_prefix', '- ')
        kwargs.setdefault('req_note_level', 'section')
        return Pysform.render(self, **kwargs)
        