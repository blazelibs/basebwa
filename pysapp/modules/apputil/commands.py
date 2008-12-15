from pysmvt import modimportauto
modimportauto('users.actions', 'permission_add')

def init_module():
    permission_add(name=u'webapp-controlpanel', safe='unique')
