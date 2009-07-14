from pysmvt import appimport

# Don't use global dependant objects here.  This code will get ran before the
# WSGI application gets setup.

def setup_package():
    setup_db_structure = appimport('testing', 'setup_db_structure')
    setup_db_structure()