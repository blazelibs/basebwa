from pysmvt.view import HtmlTemplateSnippet, HtmlTemplatePage, \
        RespondingViewBase, TextTemplateSnippet
from pysmvt import user, ag, redirect, modimport
from pysmvt.utils import tolist
from pysmvt.routing import url_for
from pysmvt.htmltable import Table, Links, A
from werkzeug.exceptions import Unauthorized, Forbidden

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
        self._call_methods_stack.append({'method_name':'auth', 'assign_args':True})
        self._call_methods_stack.append({'method_name':'check_if_authorized', 'assign_args':False})
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
        
    def get_safe_objname(self):
        return self.objectname.replace(' ', '_')
    sobjname = property(get_safe_objname)
    
    def get_action(self, actname):
        localvalue = getattr(self, '_cb_action_%s' % actname)
        if localvalue:
            return localvalue
        actions = modimport( '%s.actions' % self.modulename)
        func = '%s_%s' % (self.sobjname, actname)
        try:
            return getattr(actions, func)
        except AttributeError, e:
            if ("has no attribute '%s'" % func) not in str(e):
                raise
            # we assume the calling object will override action_get
            return None
    def get_action_get(self):
        return self.get_action('get')
    def get_action_update(self):
        return self.get_action('update')
    def get_action_delete(self):
        return self.get_action('delete')
    def get_action_list(self):
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
    def prep(self, modulename, objectname, classname ):
        actions = modimport('%s.actions' % modulename)
        forms = modimport('%s.forms' % modulename)
        self.modulename = modulename
        self.require = '%s-manage' % modulename
        self.template_name = 'common/Update'
        self.objectname = objectname
        self.message_add = '%(objectname)s added successfully'
        self.message_edit = '%(objectname)s edited successfully'
        self.message_exists_not = 'the requested %(objectname)s does not exist'
        self.endpoint_manage = '%s:%sManage' % (modulename, classname)
        self.formcls = getattr(forms, '%sForm' % classname)
        self.pagetitle = '%(actionname)s %(objectname)s'
        
    def setup(self, id):
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
            redirect(url_for(self.endpoint_manage))
        if self.form.is_valid():
            try:
                self.do_update(id)
                return
            except Exception, e:
                # if the form can't handle the exception, re-raise it
                if not self.form.handle_exception(e):
                    raise
        elif not self.form.is_submitted():
            # form was not valid, nothing left to do
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

    def default(self, id):
        
        self.assign('actionname', self.actionname)
        self.assign('objectname', self.objectname)
        self.assign('pagetitle', self.pagetitle % {'actionname':self.actionname, 'objectname':self.objectname})
        self.assign('formobj', self.form)

class ManageCommon(CommonBase):
    def prep(self, modulename, objectname, objectnamepl, classname):
        self.modulename = modulename
        self.require = '%s-manage' % modulename
        actions = modimport('%s.actions' % modulename)
        self.template_name = 'common/Manage'
        self.objectname = objectname
        self.objectnamepl = objectnamepl
        self.endpoint_update = '%s:%sUpdate' % (modulename, classname)
        self.endpoint_delete = '%s:%sDelete' % (modulename, classname)
        self.table = Table(class_='dataTable manage')

        # messages that will normally be ok, but could be overriden
        self.pagetitle = 'Manage %(objectnamepl)s'
    
    def create_table(self):
        self.table.actions = \
            Links( 'Actions',
                A(self.endpoint_delete, 'id', label='(delete)', class_='delete_link', title='delete %s' % self.objectname),
                A(self.endpoint_update, 'id', label='(edit)', class_='edit_link', title='edit %s' % self.objectname),
                width_th='8%'
             )
                       
    def default(self):
        self.create_table()
        self.assign('tablehtml', self.table.render(self.action_list()))
        self.assign('pagetitle', self.pagetitle % {'objectnamepl':self.objectnamepl} )
        self.assign('update_endpoint', self.endpoint_update)
        self.assign('objectname', self.objectname)
        self.assign('objectnamepl', self.objectnamepl)

class DeleteCommon(CommonBase):
    def prep(self, modulename, objectname, classname):
        self.modulename = modulename
        self.require = '%s-manage' % modulename
        actions = modimport('%s.actions' % modulename)
        self.objectname = objectname
        self.endpoint_manage = '%s:%sManage' % (modulename, classname)
    
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
