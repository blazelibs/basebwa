from pysmvt import db
from model.orm import AuditRecord

def create_audit_record(identifier, user_id, audit_text, comments, commit_trans=False):
    dbsess = db.sess

    ar = AuditRecord()
    dbsess.add(ar)
    ar.identifier = unicode(identifier)
    ar.user_id = user_id
    ar.audit_text = unicode(audit_text)
    ar.comments = unicode(comments)

    try:
        if commit_trans:
            db.sess.commit()
        else:
            db.sess.flush()
    except Exception, e:
        db.sess.rollback()
        raise

    return ar
    
def audit_record_get(oid=None):
    return db.sess.query(AuditRecord).get(oid)

def get_audit_record_list(identifier):
    return db.sess.query(AuditRecord).filter(AuditRecord.identifier==unicode(identifier)).order_by(AuditRecord.createdts.desc(), AuditRecord.id.desc()).all()

def get_previous_audit_record(rev_id):
    a = audit_record_get(rev_id)
    return db.sess.query(AuditRecord).filter(AuditRecord.identifier==a.identifier).filter(AuditRecord.createdts<=a.createdts).filter(AuditRecord.id<a.id).order_by(AuditRecord.createdts.desc(), AuditRecord.id.desc()).first()
    