from pysmvt.script import console_broadcast

@console_broadcast
def action_apputil_initmod():
    from pysmvt import modimport
    permission_add = modimport('users.actions', 'permission_add')
    permission_add(name=u'webapp-controlpanel', safe='unique')
broadcast_initmod = action_apputil_initmod