from pysmvt import db

def action_050_audit_data():    
    from ..model.orm import AuditRecord
    db.sess.execute(AuditRecord.__table__.delete())