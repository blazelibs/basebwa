# -*- coding: utf-8 -*-
from blazeweb.globals import rg, user
from blazeform.form import Form as blazeform
from blazeweb.routing import current_url
from blazeform.util import NotGiven
from formencode.validators import FancyValidator
from formencode import Invalid
from blazeweb.utils import registry_has_object, werkzeug_multi_dict_conv

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
