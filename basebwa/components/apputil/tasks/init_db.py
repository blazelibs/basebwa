from blazeweb.tasks import attributes

try:
    # if the auth module is not available, then give a placeholder function
    # to avoid the exception
    from compstack.auth.model.orm import Permission
except ImportError:
    Permission = None

@attributes('base-data')
def action_30_base_data():
    if Permission:
        Permission.add_iu(name=u'webapp-controlpanel')
