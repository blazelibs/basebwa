from pysmvt import modimportauto
modimportauto('users.actions', 'permission_add')


def action_apputil_initmod():
    permission_add(name=u'webapp-controlpanel', safe='unique')
broadcast_initmod = action_apputil_initmod