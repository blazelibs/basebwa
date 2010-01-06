from pysmvt import db
from model.orm import AuditRecord

def create_audit_record(identifier, user_id, audit_text, comments, commit_trans=False):
    dbsess = db.sess

    ar = AuditRecord()
    dbsess.add(ar)
    ar.identifier = identifier
    ar.user_id = user_id
    ar.audit_text = audit_text
    ar.comments = comments

    try:
        if commit_trans:
            db.sess.commit()
        else:
            db.sess.flush()
    except Exception, e:
        db.sess.rollback()
        raise

def get_audit_record_list(identifier):
    return db.sess.query(AuditRecord).filter(AuditRecord.identifier==identifier).order_by(AuditRecord.createdts.desc()).all()
    