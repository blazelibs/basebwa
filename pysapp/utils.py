from pysmvt import user, forward, ag

def fatal_error(user_desc = None, dev_desc = None, orig_exception = None):
    # log stuff
    ag.logger.debug('Fatal error: "%s" -- %s', dev_desc, str(orig_exception))
    
    # set user message
    if user_desc != None:
        user.add_message('error', user_desc)
        
    # forward to fatal error view
    forward('apputil:SystemError')
    
class ControlPanelSection(object):
    
    def __init__(self, heading , has_perm, *args):
        self.heading = heading 
        self.has_perm = has_perm
        self.groups = []
        for group in args:
            self.add_group(group)

    def add_group(self, group):
        self.groups.append(group)

class ControlPanelGroup(object):
    
    def __init__(self, *args):
        self.links = []
        for link in args:
            self.add_link(link)

    def add_link(self, link):
        self.links.append(link)

class ControlPanelLink(object):
    
    def __init__(self, text, endpoint):
        self.text = text
        self.endpoint = endpoint

def run_module_sql(module, target, use_dialect=False):
    ''' used to run SQL from files in a modules "sql" directory:
    
            run_module_sql('mymod', 'create_views')
        
        will run the file "<myapp>/modules/mymod/sql/create_views.sql"
        
            run_module_sql('mymod', 'create_views', True)
        
        will run the files:
            
            # sqlite DB
            <myapp>/modules/mymod/sql/create_views.sqlite.sql
            # postgres DB
            <myapp>/modules/mymod/sql/create_views.pgsql.sql
            ...
        
        The dialect prefix used is the same as the sqlalchemy prefix.
        
        The SQL file can contain multiple statements.  They should be seperated
        with the text "--statement-break".
            
    '''
    from pysmvt import db, appfilepath
    from os.path import join

    if use_dialect:
        relative_sql_path = 'modules/%s/sql/%s.%s.sql' % (module, target, db.engine.dialect.name )
    else:
        relative_sql_path = 'modules/%s/sql/%s.sql' % (module, target )
    
    full_path = appfilepath(relative_sql_path)
    
    sqlfile = file(full_path)
    sql = sqlfile.read()
    sqlfile.close()
    for statement in sql.split('--statement-break'):
        statement.strip()
        if statement:
            db.sess.execute(statement)
    db.sess.commit()