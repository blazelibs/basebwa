from pysmvt import modimport

def action_30_base_data():    
    permission_add = modimport('users.actions', 'permission_add')
    permission_add(name=u'webapp-controlpanel', safe='unique')