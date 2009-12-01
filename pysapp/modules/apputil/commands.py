from pysmvt import modimport
from pysmvt.script import console_broadcast

@console_broadcast
def action_apputil_initdb():
    permission_add = modimport('users.actions', 'permission_add')
    permission_add(name=u'webapp-controlpanel', safe='unique')