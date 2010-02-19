# -*- coding: utf-8 -*-
from pysmvt import rg, user
from pysform.form import Form as Pysform
from pysmvt.routing import current_url
from pysform.util import NotGiven
from formencode.validators import FancyValidator
from formencode import Invalid

class Form(Pysform):
    note_prefix = '- '
    error_prefix = '- '
    req_note_level = 'section'
    req_note = None
    
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
        if not self._request_submitted and not self._static:
            tosubmit = {}
            try:
                for key, value in rg.request.form.to_dict(flat=False).iteritems():
                    if len(value) == 1:
                        tosubmit[key] = value[0]
                    else:
                        tosubmit[key] = value
                tosubmit.update(rg.request.files.to_dict())
                self.set_submitted(tosubmit)
            except TypeError, e:
                if 'has been registered for this thread' not in str(e):
                    raise
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
        if self.note_prefix:
            kwargs.setdefault('note_prefix', self.note_prefix)
        if self.error_prefix:
            kwargs.setdefault('error_prefix', self.error_prefix)
        if self.req_note_level:
            kwargs.setdefault('req_note_level', self.req_note_level)
        if self.req_note:
            kwargs.setdefault('req_note', self.req_note)
        return Pysform.render(self, **kwargs)

class UniqueValidator(FancyValidator):
    """
    Calls the given callable with the value of the field.  If the return value
    does not evaluate to false, Invalid is raised
    """
    
    __unpackargs__ = ('fn')
    messages = {
        'notunique': "the value for this field must be unique",
        }

    def validate_python(self, value, state):
        if value == state.defaultval:
            return
        if self.fn(value):
            raise Invalid(self.message('notunique', state), value, state)
        return