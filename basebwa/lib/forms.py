from blazeweb.routing import url_for
from savalidation import ValidationError
from webhelpers.html.tags import link_to

from compstack.common.lib.forms import Form as CommonForm

class Form(CommonForm):
    def __init__(self, name=None, **kwargs):
        CommonForm.__init__(self, name, **kwargs)
        self.add_handler(exc_type=ValidationError, callback=self.handle_validation_error)

    def handle_validation_error(self, exc):
        # used to indicate if all errors were assignable for at least one instance.
        # If not, consider handling the validation to have failed
        all_errors_handled = False
        for inst in exc.invalid_instances:
            if self.add_field_errors(inst.validation_errors):
                all_errors_handled = True
        return all_errors_handled

class LookupMixin(object):
    def add_active_flag(self):
        return self.add_checkbox('active_flag', 'Active', defaultval=True)

    def add_label(self):
        return self.add_text('label', 'Label', required=True)

    def add_submit(self, crud_view=None):
        sg = self.add_elgroup('submit-group', class_='submit-only')
        sg.add_submit('submit')
        crud_view = crud_view or self.__class__.__name__ + 'Crud'
        sg.add_static('cancel', None, link_to('Cancel', url_for(crud_view, action='manage'), title='Go back to the manage page'))
        return sg

    def add_lookup_fields(self, crud_view=None):
        return self.add_label(), \
            self.add_active_flag(), \
            self.add_submit(crud_view)
