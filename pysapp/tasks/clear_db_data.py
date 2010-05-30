from pysmvt import db

def action_000_task_begin():  
    db.sess.commit()

def action_100_task_commit():
    db.sess.commit()