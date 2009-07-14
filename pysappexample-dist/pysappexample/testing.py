from pysmvt.commands import manual_broadcast
from pysmvt.script import _gather_actions

# if running tests in supporting applications, those applications should be
# doing:
#
#   def setup_package():
#       setup_db_structure = appimport('testing', 'setup_db_structure')
#       setup_db_structure()
#
# in the application package's __init__.py file.  This allows supporting
# applications to make sure the db gets setup before their tests are run.  This
# means setup_db_structure() can be called more than once since it would get
# called for the primary applications and supporting applications, we want to
# make sure we only do the db structure init once.
_setup_db_structure_ran = False

def setup_db_structure():
    """
        This method sets up a proper database structure for tests. It does not
        put any data in the structures.  This is because each test should have
        the freedom to create/destroy data at will.
    """
    global _setup_db_structure_ran
    if not _setup_db_structure_ran:
        actions = _gather_actions()
        manual_broadcast('initdb')
        _setup_db_structure_ran = True
    