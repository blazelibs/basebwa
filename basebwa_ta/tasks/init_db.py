from compstack.auth.model.orm import Permission

def action_30_perms():
    Permission.add_iu(name=u'widget-delete')
