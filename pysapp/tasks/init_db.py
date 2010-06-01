from pysmvt import db
from sqlitefktg4sa import auto_assign

def action_10_create_db_objects():
    """ initialize the database """
    # create foreign keys for SQLite
    auto_assign(db.meta, db.engine)

    # create the database objects
    db.meta.create_all(bind=db.engine)