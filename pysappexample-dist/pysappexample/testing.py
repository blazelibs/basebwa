from applications import make_wsgi
from pysmvt.commands import manual_broadcast
from pysmvt.script import _gather_actions

testapp = make_wsgi('Test')

def setup_db_structure():
    """
        This method sets up a proper database structure for tests. It does not
        put any data in the structures.  This is because each test should have
        the freedom to create/destroy data at will.
    """
    actions = _gather_actions()
    manual_broadcast('initdb')
    