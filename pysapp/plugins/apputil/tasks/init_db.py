from pysmvt.tasks import attributes

from plugstack.auth.actions import permission_update

@attributes('base-data')
def action_30_base_data():
    permission_update(None, name=u'webapp-controlpanel', _ignore_unique_exception=True)
