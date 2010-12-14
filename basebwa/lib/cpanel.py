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
        takes a blazeweb.user:User object and ControlPanelSections for *args
        and sets the user_has_perm attribute on the ControlPanelSection,
        ControlPanelGroup, and ControlPanelList objects as appropriate.
    """
    retval = []
    for sec in sections:
        sec_groups = []
        if sec.has_perm and not session_user.has_any_perm(sec.has_perm):
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
