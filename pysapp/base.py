from pysmvt.view import HtmlTemplateSnippet, HtmlTemplatePage, \
        RespondingViewBase, TextTemplateSnippet
from pysmvt import user, ag, redirect, modimport, settings
from pysmvt.utils import tolist, traceback_depth, tb_depth_in
from pysmvt.routing import url_for
from pysmvt.htmltable import Table, Links, A
from werkzeug.exceptions import Unauthorized, Forbidden
from pysmvt.exceptions import ProgrammingError

class BaseViewMixin(object):
    def __init__(self):
        self._call_methods_stack.append({'method_name':'setup', 'assign_args':True})
        
class ProtectedViewMixin(BaseViewMixin):
    def __init__(self):
        # Default to not show the view
        self.is_authenticated = False
        self.is_authorized = False
        # if True, don't check permissions, just require user to be authorized
        self.authenticated_only = False
        # if both of the above are false, require the user to have at least
        # one of the following permissions
        self.require = ()
        # we want setup() at the front of the call methods
        BaseViewMixin.__init__(self)
        # setup the methods that will be called
        self._call_methods_stack.append({'method_name':'pre_auth_setup', 'assign_args':True})
        self._call_methods_stack.append({'method_name':'auth', 'assign_args':True})
        self._call_methods_stack.append({'method_name':'check_if_authorized', 'assign_args':False})
        self._call_methods_stack.append({'method_name':'post_auth_setup', 'assign_args':True})
        self._call_methods_stack.append({'method_name':'postauth', 'assign_args':True})
        
    def auth(self, **kwargs):
        if user.is_authenticated():
            self.is_authenticated = True
    
        if self.authenticated_only:
            self.is_authorized = True
        elif user.get_attr('super_user'):
            self.is_authorized = True
        else:
            for perm in tolist(self.require):
                if user.has_perm(perm):
                    self.is_authorized = True

    def check_if_authorized(self):
        if not self.is_authenticated:
            raise Unauthorized()
        if not self.is_authorized:
            raise Forbidden()
        

class PublicSnippetView(HtmlTemplateSnippet, BaseViewMixin):
    """ HTML snippet with template support that allows public access """
    def __init__(self, modulePath, endpoint, args):
        HtmlTemplateSnippet.__init__(self, modulePath, endpoint, args)
        BaseViewMixin.__init__(self)

class PublicTextSnippetView(TextTemplateSnippet, BaseViewMixin):
    """ TEXT snippet with template support that allows public access """
    def __init__(self, modulePath, endpoint, args):
        TextTemplateSnippet.__init__(self, modulePath, endpoint, args)
        BaseViewMixin.__init__(self)

class PublicPageView(HtmlTemplatePage, BaseViewMixin):
    """ HTML page with template support that allows public access """
    def __init__(self, modulePath, endpoint, args):
        HtmlTemplatePage.__init__(self, modulePath, endpoint, args)
        BaseViewMixin.__init__(self)

class ProtectedSnippetView(HtmlTemplateSnippet, ProtectedViewMixin):
    """ HTML snippet with template support that has protected access """
    def __init__(self, modulePath, endpoint, args):
        HtmlTemplateSnippet.__init__(self, modulePath, endpoint, args)
        ProtectedViewMixin.__init__(self)

class ProtectedPageView(HtmlTemplatePage, ProtectedViewMixin):
    """ HTML page with template support that has protected access """
    def __init__(self, modulePath, endpoint, args):
        HtmlTemplatePage.__init__(self, modulePath, endpoint, args)
        ProtectedViewMixin.__init__(self)

class ProtectedRespondingView(RespondingViewBase, ProtectedViewMixin):
    """ Responding view (no template support) that has protected access """
    def __init__(self, modulePath, endpoint, args):
        RespondingViewBase.__init__(self, modulePath, endpoint, args)
        ProtectedViewMixin.__init__(self)
        
class CommonBase(ProtectedPageView):
    def __init__(self, *args, **kwargs ):
        ProtectedPageView.__init__(self, *args, **kwargs)
        self._cb_action_get = None
        self._cb_action_update = None
        self._cb_action_delete = None
        self._cb_action_list = None
        
    def get_safe_action_prefix(self):
        return self.action_prefix.replace(' ', '_')
    safe_action_prefix = property(get_safe_action_prefix)
    
    def get_action(self, actname):
        localvalue = getattr(self, '_cb_action_%s' % actname)
        if localvalue:
            return localvalue
        func = '%s_%s' % (self.safe_action_prefix, actname)
        try:
            return modimport( '%s.actions' % self.modulename, func)
        except ImportError, e:
            if not tb_depth_in(3):
                raise
            # we assume the calling object will override action_get
            return None
    def test_action(self, actname):
        callable = self.get_action(actname)
        if callable is None:
            func = '%s_%s' % (self.safe_action_prefix, actname)
            raise ProgrammingError('The default "%s" function `%s` was not found.'
                                   % (actname, func))
    def get_action_get(self):
        self.test_action('get')
        return self.get_action('get')
    def get_action_update(self):
        self.test_action('update')
        return self.get_action('update')
    def get_action_delete(self):
        self.test_action('delete')
        return self.get_action('delete')
    def get_action_list(self):
        self.test_action('list')
        return self.get_action('list')
    def set_action_get(self, value):
        self._cb_action_get = value
    def set_action_update(self, value):
        self._cb_action_update = value
    def set_action_delete(self, value):
        self._cb_action_delete = value
    def set_action_list(self, value):
        self._cb_action_list = value
        
    action_get = property(get_action_get, set_action_get)
    action_update = property(get_action_update, set_action_update)
    action_delete = property(get_action_delete, set_action_delete)
    action_list = property(get_action_list, set_action_list)
    
class UpdateCommon(CommonBase):
    def prep(self, modulename, objectname, classname, action_prefix=None):
        self.modulename = modulename
        self.require = '%s-manage' % modulename
        self.template_name = 'common/Update'
        self.objectname = objectname
        self.message_add = '%(objectname)s added successfully'
        self.message_edit = '%(objectname)s edited successfully'
        self.message_exists_not = 'the requested %(objectname)s does not exist'
        self.endpoint_manage = '%s:%sManage' % (modulename, classname)
        self.formcls = modimport('%s.forms' % modulename, '%sForm' % classname)
        self.pagetitle = '%(actionname)s %(objectname)s'
        self.extend_from = settings.template.admin
        self.action_prefix = action_prefix or objectname
        
    def post_auth_setup(self, id):
        self.determine_add_edit(id)
        self.assign_form()
        self.do_if_edit(id)        

    def determine_add_edit(self, id):
        if id is None:
            self.isAdd = True
            self.actionname = 'Add'
            self.message_update = self.message_add % {'objectname':self.objectname}
        else:
            self.isAdd = False
            self.actionname = 'Edit'
            self.message_update = self.message_edit % {'objectname':self.objectname}
            
    def assign_form(self):
        self.form = self.formcls()
        
    def do_if_edit(self, id):
        if not self.isAdd:
            dbobj = self.action_get(id)
            
            if dbobj is None:
                user.add_message('error', self.message_exists_not % {'objectname':self.objectname})
                self.on_edit_error()
                
            self.form.set_defaults(dbobj.to_dict())
    
    def on_edit_error(self):
        self.on_complete()
    
    def post(self, id):        
        self.form_submission(id)
        self.default(id)
    
    def form_submission(self, id):
        if self.form.is_cancel():
            self.on_cancel()
        if self.form.is_valid():
            try:
                self.do_update(id)
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
    
    def do_update(self, id):
        self.action_update(id, **self.form.get_values())
        user.add_message('notice', self.message_update)
        self.on_complete()
    
    def on_complete(self):
        url = url_for(self.endpoint_manage)
        redirect(url)
    
    def on_cancel(self):
        redirect(url_for(self.endpoint_manage))
    
    def default(self, id):
        
        self.assign('actionname', self.actionname)
        self.assign('objectname', self.objectname)
        self.assign('pagetitle', self.pagetitle % {'actionname':self.actionname, 'objectname':self.objectname})
        self.assign('formobj', self.form)
        self.assign('extend_from', self.extend_from)

class ManageCommon(CommonBase):
    def prep(self, modulename, objectname, objectnamepl, classname, action_prefix=None):
        self.modulename = modulename
        self.require = '%s-manage' % modulename
        self.delete_link_require = '%s-manage' % modulename
        self.template_name = 'common/Manage'
        self.objectname = objectname
        self.objectnamepl = objectnamepl
        self.endpoint_update = '%s:%sUpdate' % (modulename, classname)
        self.endpoint_delete = '%s:%sDelete' % (modulename, classname)
        self.table = Table(class_='dataTable manage')
        self.extend_from = settings.template.admin
        self.action_prefix = action_prefix or objectname
        
        # messages that will normally be ok, but could be overriden
        self.pagetitle = 'Manage %(objectnamepl)s'
    
    def create_table(self):
        if user.has_any_perm(self.delete_link_require):
            self.table.actions = \
                Links( 'Actions',
                    A(self.endpoint_delete, 'id', label='(delete)', class_='delete_link', title='delete %s' % self.objectname),
                    A(self.endpoint_update, 'id', label='(edit)', class_='edit_link', title='edit %s' % self.objectname),
                    width_th='8%'
                 )
        else:
            self.table.actions = \
                Links( 'Actions',
                    A(self.endpoint_update, 'id', label='(edit)', class_='edit_link', title='edit %s' % self.objectname),
                    width_th='8%'
                 )
    
    def render_table(self):
        data = self.action_list()
        self.assign('tablehtml', self.table.render(data))
    
    def default(self):
        self.create_table()
        self.render_table()
        self.assign('pagetitle', self.pagetitle % {'objectnamepl':self.objectnamepl} )
        self.assign('update_endpoint', self.endpoint_update)
        self.assign('objectname', self.objectname)
        self.assign('objectnamepl', self.objectnamepl)
        self.assign('extend_from', self.extend_from)

class DeleteCommon(CommonBase):
    def prep(self, modulename, objectname, classname, action_prefix=None):
        self.modulename = modulename
        self.require = '%s-manage' % modulename
        actions = modimport('%s.actions' % modulename)
        self.objectname = objectname
        self.endpoint_manage = '%s:%sManage' % (modulename, classname)
        self.action_prefix = action_prefix or objectname
    
        # messages that will normally be ok, but could be overriden
        self.message_ok = '%(objectname)s deleted'
        self.message_error = '%(objectname)s was not found'
        
    def default(self, id):
        if self.action_delete(id):
            user.add_message('notice', self.message_ok % {'objectname':self.objectname})
        else:
            user.add_message('error', self.message_error % {'objectname':self.objectname})
            
        url = url_for(self.endpoint_manage)
        redirect(url)
