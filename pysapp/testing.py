from pysmvt.commands import manual_broadcast
from pysmvt.script import _gather_actions
from pysmvt import appimportauto
appimportauto('lib.db', 'clear_db')

def setup_db_structure():
    """
        This method sets up a proper database structure for tests. It does not
        put any data in the structures.  This is because each test should have
        the freedom to create/destroy data at will.
        
        If a settings is configured like:
            
            self.testing.init_callables = 'testing.setup_db_structure'
            
        This function will be called once by nose after the application
        object is initilzed but before any tests are ran.
    """
    actions = _gather_actions()
    clear_db()
    manual_broadcast('initdb')
    