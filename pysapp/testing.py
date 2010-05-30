from pysmvt.tasks import run_tasks

def setup_db_structure():
    """
        This function sets up a database for running unit and functional tests.
        It is called by the pysmvt nose plugin if there is a setting in the
        application like:
            
            self.testing.init_callables = 'testing.setup_db_structure'
            
        This function will be called once by nose after the application
        object is initilzed but before any tests are ran.
    """
    run_tasks(('clear-db', 'init-db:~test'))
    