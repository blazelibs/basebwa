from pysmvt import db
from sqlitefktg4sa import auto_assign

def action_pysapp_initdb(sqlite_triggers=True):
    """ initialize the database """
    # create foreign keys for SQLite
    if sqlite_triggers and not getattr(db.meta, 'triggers', False):
        auto_assign(db.meta, db.engine)
        db.meta.triggers = True

    # create the database objects
    #print db
    #for t in db.meta.tables:
    #    print t
    db.meta.create_all(bind=db.engine)
    
    # add a session to the db
    #db.sess = db.Session()
broadcast_initdb = action_pysapp_initdb