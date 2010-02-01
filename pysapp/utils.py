from decorator import decorator
import warnings
from pysutils import decorator
from pysmvt import user, forward, ag, db
from pysapp import exc
from pysapp.lib import db as libdb

class ControlPanelSection(object):
    
    def __init__(self, heading , has_perm, *args):
        self.heading = heading 
        self.has_perm = has_perm
        self.groups = []
        for group in args:
            self.add_group(group)

    def add_group(self, group):
        self.groups.append(group)
        
    def __repr__(self):
        return 'ControlPanelSection: %s; %s' % (self.heading, self.groups)

class ControlPanelGroup(object):
    
    def __init__(self, *args, **kwargs):
        self.links = []
        for link in args:
            self.add_link(link)
        self.has_perm = kwargs.get('has_perm', None)
        
    def add_link(self, link):
        self.links.append(link)
        
    def __repr__(self):
        return 'ControlPanelGroup: %s' % self.links

class ControlPanelLink(object):
    
    def __init__(self, text, endpoint, **kwargs):
        self.text = text
        self.endpoint = endpoint
        self.has_perm = kwargs.get('has_perm', None)
        if kwargs.has_key('has_perm'):
            del kwargs['has_perm']
        self.linkargs = kwargs
        
    def __repr__(self):
        return 'ControlPanelLink: %s -> %s' % (self.text, self.endpoint)

def control_panel_permission_filter(session_user, *sections):
    """
        takes a pysmvt.user:User object and ControlPanelSections for *args
        and sets the user_has_perm attribute on the ControlPanelSection,
        ControlPanelGroup, and ControlPanelList objects as appropriate.
    """
    retval = []
    for sec in sections:
        sec_groups = []
        if sec.has_perm and not session_user.has_perm(sec.has_perm):
            continue
        for lg in sec.groups:
            group_links = []
            if lg.has_perm and not session_user.has_perm(lg.has_perm):
                continue
            for link in lg.links:
                if session_user.has_perm(link.has_perm) or not link.has_perm:
                    group_links.append(link)
            if group_links:
                sec_groups.append({'group': lg, 'group_links' : group_links})
        if sec_groups:
            retval.append({'sec': sec, 'sec_groups' : sec_groups})
    return retval

def warn(msg):
    if isinstance(msg, basestring):
        warnings.warn(msg, exc.PysappWarning, stacklevel=3)
    else:
        warnings.warn(msg, stacklevel=3)

def warn_deprecated(msg):
    warnings.warn(msg, exc.PysappDeprecationWarning, stacklevel=3)

def warn_pending_deprecation(msg):
    warnings.warn(msg, exc.PysappPendingDeprecationWarning, stacklevel=3)

def deprecated(message=None, add_deprecation_to_docstring=True):
    """Decorates a function and issues a deprecation warning on use.

    message
      If provided, issue message in the warning.  A sensible default
      is used if not provided.

    add_deprecation_to_docstring
      Default True.  If False, the wrapped function's __doc__ is left
      as-is.  If True, the 'message' is prepended to the docs if
      provided, or sensible default if message is omitted.
    """

    if add_deprecation_to_docstring:
        header = message is not None and message or 'Deprecated.'
    else:
        header = None

    if message is None:
        message = "Call to deprecated function %(func)s"

    def decorate(fn):
        return _decorate_with_warning(
            fn, exc.PysappDeprecationWarning,
            message % dict(func=fn.__name__), header)
    return decorate

def pending_deprecation(version, message=None,
                        add_deprecation_to_docstring=True):
    """Decorates a function and issues a pending deprecation warning on use.

    version
      An approximate future version at which point the pending deprecation
      will become deprecated.  Not used in messaging.

    message
      If provided, issue message in the warning.  A sensible default
      is used if not provided.

    add_deprecation_to_docstring
      Default True.  If False, the wrapped function's __doc__ is left
      as-is.  If True, the 'message' is prepended to the docs if
      provided, or sensible default if message is omitted.
    """

    if add_deprecation_to_docstring:
        header = message is not None and message or 'Deprecated.'
    else:
        header = None

    if message is None:
        message = "Call to deprecated function %(func)s"

    def decorate(fn):
        return _decorate_with_warning(
            fn, exc.PysappPendingDeprecationWarning,
            message % dict(func=fn.__name__), header)
    return decorate

def _decorate_with_warning(func, wtype, message, docstring_header=None):
    """Wrap a function with a warnings.warn and augmented docstring."""

    @decorator
    def warned(fn, *args, **kwargs):
        warnings.warn(wtype(message), stacklevel=3)
        return fn(*args, **kwargs)

    doc = func.__doc__ is not None and func.__doc__ or ''
    if docstring_header is not None:
        docstring_header %= dict(func=func.__name__)
        docs = doc and doc.expandtabs().split('\n') or []
        indent = ''
        for line in docs[1:]:
            text = line.lstrip()
            if text:
                indent = line[0:len(line) - len(text)]
                break
        point = min(len(docs), 1)
        docs.insert(point, '\n' + indent + docstring_header.rstrip())
        doc = '\n'.join(docs)

    decorated = warned(func)
    decorated.__doc__ = doc
    return decorated

def excignore(f, *args, **kwargs):
    """
        If _excignore has a value and if the function throws an exception with the
        str(_excignore) in the error message, the exception will be ignored.
        Useful when initializing data with add or update methods.
    """
    def innerfunc(*args, **kwargs):
        _excignore = kwargs.pop('_excignore', None)
        try:
            return f(*args, **kwargs)
        except Exception, e:
            if not _excignore or _excignore not in str(e).lower():
                raise
            db.sess.rollback()
    return innerfunc
    

############### DEPRECATED FUNCTIONS #########################
@deprecated('use pysapp.lib.db.run_module_sql instead')
def run_module_sql(module, target, use_dialect=False):
    libdb.run_module_sql(module, target, use_dialect)

@deprecated('use pysapp.lib.db.run_app_sql instead')
def run_app_sql(target, use_dialect=False):
    libdb.run_app_sql(target, use_dialect)
    
@deprecated('raise the appropriate HTTP exception instead')
def fatal_error(user_desc = None, dev_desc = None, orig_exception = None):
    # log stuff
    ag.logger.debug('Fatal error: "%s" -- %s', dev_desc, str(orig_exception))
    
    # set user message
    if user_desc != None:
        user.add_message('error', user_desc)
        
    # forward to fatal error view
    forward('apputil:SystemError')