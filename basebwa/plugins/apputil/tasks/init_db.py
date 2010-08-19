from blazeweb.tasks import attributes

try:
    # if the auth module is not available, then give a placeholder function
    # to avoid the exception
    from plugstack.auth.model.actions import permission_update
except ImportError:
    def permission_update(*args, **kwargs):
        pass

@attributes('base-data')
def action_30_base_data():
    permission_update(None, name=u'webapp-controlpanel', _ignore_unique_exception=True)
