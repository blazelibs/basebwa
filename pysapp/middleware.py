
from pysmvt import db, settings
from sqlalchemy import engine_from_config, MetaData
from pysmvt.hierarchy import visitmods
from sqlalchemy.orm import sessionmaker, scoped_session

class SQLAlchemyContainer(object):

    def __init__(self):
        self.engine = engine_from_config(dict(settings.db), prefix='')
        self.meta = MetaData()
        self.Session = scoped_session(sessionmaker(
                bind=self.engine,
                autoflush=False,
            ))

    def get_session(self):
        return self.Session()

class SQLAlchemyApp(object):
    """
        Creates an Sqlalchemy Engine and Metadata for the application

        Sets up thread-local sessions and cleans them up per request
    """
    def __init__(self, application):
        self.application = application
        self.container = SQLAlchemyContainer()
        db._push_object(self.container)
        print 'created db'
        db.sess = self.container.Session
        visitmods('model.orm')
        visitmods('model.metadata')

    def __call__(self, environ, start_response):
        def response_cycle_teardown():
            self.container.Session.remove()
        environ.setdefault('pysmvt.response_cycle_teardown', [])
        environ['pysmvt.response_cycle_teardown'].append(response_cycle_teardown)
        return self.application(environ, start_response)
