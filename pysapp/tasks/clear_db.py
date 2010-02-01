from pysmvt import appimport

def action_50_drop_db_objects():
    clear_db = appimport('lib.db', 'clear_db')
    clear_db()