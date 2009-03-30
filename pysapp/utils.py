from pysmvt import user, forward, ag

def fatal_error(user_desc = None, dev_desc = None, orig_exception = None):
    # log stuff
    ag.logger.debug('Fatal error: "%s" -- %s', dev_desc, str(orig_exception))
    
    # set user message
    if user_desc != None:
        user.add_message('error', user_desc)
        
    # forward to fatal error view
    forward('apputil:SystemError')
    
class ControlPanelSection(object):
    
    def __init__(self, heading , has_perm, *args):
        self.heading = heading 
        self.has_perm = has_perm
        self.groups = []
        for group in args:
            self.add_group(group)

    def add_group(self, group):
        self.groups.append(group)

class ControlPanelGroup(object):
    
    def __init__(self, *args):
        self.links = []
        for link in args:
            self.add_link(link)

    def add_link(self, link):
        self.links.append(link)

class ControlPanelLink(object):
    
    def __init__(self, text, endpoint):
        self.text = text
        self.endpoint = endpoint