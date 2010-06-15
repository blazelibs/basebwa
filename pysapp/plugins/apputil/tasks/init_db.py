from pysmvt.tasks import attributes

from plugstack.auth.actions import permission_add

@attributes('base-data')
def action_30_base_data():
    permission_add(name=u'webapp-controlpanel', safe='unique')
