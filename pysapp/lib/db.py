import logging
from os.path import join
from decorator import decorator
from pysutils import curry
from pysmvt import db
import sqlalchemy.types
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.ext.declarative import declarative_base, \
    DeclarativeMeta, _declarative_constructor

log = logging.getLogger(__name__)

__all__ = [
    'NestedSetExtension',
    'DeclarativeMixin'
]

class NestedSetException(Exception):
    """ Base class for nested set related exceptions """
    
class MultipleRootsError(NestedSetException):
    """ Used when a root node is requested but a root node already exists
        in the table.
    """
    
class MultipleAnchorsError(NestedSetException):
    """
        Used when a node has more than one anchor point.
    """
        
class MultipleDeletesError(NestedSetException):
    """
        Can only delete one node at a time.  Issue a commit() between
        deletes.
    """
    
class MultipleUpdatesError(NestedSetException):
    """
        Can only update one node at a time.  Issue a commit() between
        updates.
    """

class NestedSetExtension(MapperExtension):
    
    _node_delete_count = 0
    _node_update_count = 0
    
    def __init__(self, pkname='id'):
        self.pkname = pkname
        
    def before_insert(self, mapper, connection, instance):        
        nodetbl = mapper.mapped_table
        
        # only one anchor can be given
        anchor_count = 0
        if instance.parent:
            anchor_count += 1
        if instance.upper_sibling:
            anchor_count += 1
        if instance.lower_sibling:
            anchor_count += 1
        if anchor_count > 1:
            raise MultipleAnchorsError('Nested set nodes can only have one anchor (parent, upper sibling, or lower sibling)')
        
        # set values for the instance node
        if anchor_count == 0:
            """ This is a root node """
            
            # test to make sure no other root nodes exist.  Since we don't have
            # treeids currently, we can't do multiple trees.
            rootnode = connection.execute(
                    select([nodetbl]).where(nodetbl.c.parentid == None)
                ).fetchone()
            if rootnode:
                raise MultipleRootsError('Multiple root nodes are not supported.')
                
            # set node values
            nleft = 1
            nright = 2
            ndepth = 1
            #ntreeid = None
            nparentid = None
        else:
            if instance.parent:
                    
                ancnode = connection.execute(
                    select([nodetbl]).where(getattr(nodetbl.c, self.pkname) == getattr(instance.parent, self.pkname))
                ).fetchone()
                
                # The parent, and all nodes to the "right" will need to be adjusted
                shift_inclusion_boundary = ancnode.redge
                # All nodes to the "right" but NOT the parent will need their
                # left edges adjusted
                ledge_inclusion_boundary = ancnode.redge + 1
                # The left edge of the new node is where the right edge of the parent
                # used to be
                nleft = ancnode.redge
                # children increase depth
                ndepth = ancnode.depth + 1
                # parent
                nparentid = getattr(ancnode, self.pkname)
            else:
                if instance.upper_sibling:
                    ancnode = connection.execute(
                        select([nodetbl]).where(getattr(nodetbl.c, self.pkname) == getattr(instance.upper_sibling, self.pkname))
                    ).fetchone()
                    # Nodes to the "right" of anchor and the parent will need
                    # to be adjusted
                    shift_inclusion_boundary = ancnode.redge + 1
                    # Nodes to the "right" of anchor but NOT the parent will
                    # need their left edges adjusted
                    ledge_inclusion_boundary = ancnode.redge + 1
                    # The new node will be just to the "right" of the anchor
                    nleft = ancnode.redge+1
                else:
                    ancnode = connection.execute(
                        select([nodetbl]).where(getattr(nodetbl.c, self.pkname) == getattr(instance.lower_sibling, self.pkname))
                    ).fetchone()
                    # The anchor, all its children, and the parent will need
                    # to be adjusted
                    shift_inclusion_boundary = ancnode.redge
                    # The anchor, all its children, but NOT the parent will
                    # need the left edge adjusted
                    ledge_inclusion_boundary = ancnode.ledge
                    # The new node takes the place of the anchor node
                    nleft = ancnode.ledge
                # siblings have the same depth
                ndepth = ancnode.depth
                # parent
                nparentid = ancnode.parentid
            
            # new nodes have no children
            nright = nleft + 1
            # treeid is always the same
            #ntreeid = ancnode.treeid
            
            connection.execute(
                nodetbl.update() \
                    .where(
                        #and_(
                        #    nodetbl.c.treeid == ntreeid,
                        #    nodetbl.c.redge >= shift_inclusion_boundary
                        #    )
                        nodetbl.c.redge >= shift_inclusion_boundary
                    ).values(
                        ledge = case(
                                [(nodetbl.c.ledge >= ledge_inclusion_boundary, nodetbl.c.ledge + 2)],
                                else_ = nodetbl.c.ledge
                              ),
                        redge = nodetbl.c.redge + 2
                    )
            )

        #instance.treeid = ntreeid
        instance.ledge = nleft
        instance.redge = nleft + 1
        instance.parentid = nparentid
        instance.depth = ndepth

    def before_update(self, mapper, connection, instance):
        nodetbl = mapper.mapped_table
        self._node_update_count += 1
        try:
            # only one anchor can be given
            anchor_count = 0
            if instance.parent:
                anchor_count += 1
                anchor = instance.parent
            if instance.upper_sibling:
                anchor_count += 1
                anchor = instance.upper_sibling
            if instance.lower_sibling:
                anchor_count += 1
                anchor = instance.lower_sibling
            if anchor_count > 1:
                raise MultipleAnchorsError('Nested set nodes can only have one anchor (parent, upper sibling, or lower sibling)')
            if anchor_count == 0:
                log.debug('before_update: no anchor given, returning')
                """
                    assume the object is being updated for other reasons, tree position
                    is staying the same.
                """
                return
                
            # get fresh data from the DB in case this instance has been updated
            tu_node_data = connection.execute(
                            select([nodetbl]).where(getattr(nodetbl.c, self.pkname) == getattr(instance, self.pkname))
                        ).fetchone()
            tuledge = tu_node_data['ledge']
            turedge = tu_node_data['redge']
            tudepth = tu_node_data['depth']
            tuparentid = tu_node_data['parentid']
            tuwidth = turedge - tuledge + 1
            
            # get fresh anchor from the DB in case the instance was updated
            anc_node_data = connection.execute(
                            select([nodetbl]).where(getattr(nodetbl.c, self.pkname) == getattr(anchor, self.pkname))
                        ).fetchone()
            ancledge = anc_node_data['ledge']
            ancredge = anc_node_data['redge']
            ancdepth = anc_node_data['depth']
            ancparentid = anc_node_data['parentid']
            
            if getattr(anchor, self.pkname) == getattr(instance, self.pkname):
                raise NestedSetException('A nodes anchor can not be iteself.')
                
            if ancledge > tuledge and ancledge < turedge:
                raise NestedSetException('A nodes anchor can not be one of its children.')
            
            if instance.parent:
                log.debug('before_update: anchor is parent')
                # if the nodes parent is already the requested parent, do nothing
                if tuparentid == getattr(anchor, self.pkname):
                    log.debug('before_update: parent requested is already the'
                              ' current parent, returning')
                    return
                
                if tuledge > ancledge:
                    """ parent from grandchild and parent from right """
                    log.debug('before_update: parent from grandchild and parent'
                              ' from right')
                    ancledgeaftershift = ancledge
                    instance_children_shift = ancledge - tuledge + 1
                    left_bound_of_displaced  = ancledge+1
                    right_bound_of_displaced = tuledge-1
                    displaced_shift = turedge-tuledge+1
                    right_boundary_for_ledge  = turedge
                    left_boundary_for_redge = ancledge
                else:
                    """ parent from left: make sure we account for our anchor
                    point shifting. """
                    log.debug('before_update: parent from left')
                    ancledgeaftershift = ancledge - tuwidth
                    instance_children_shift = ancledge - turedge
                    left_bound_of_displaced  = turedge + 1
                    right_bound_of_displaced = ancledge
                    displaced_shift = tuwidth * -1
                    right_boundary_for_ledge  = ancledge+1
                    left_boundary_for_redge = tuledge
                children_depth = ancdepth-tudepth+1
                
                instance.parentid = getattr(anchor, self.pkname)
                instance.ledge = ancledgeaftershift + 1 
                instance.redge = instance.ledge + tuwidth - 1
                instance.depth = ancdepth + 1
            else:
                if ancparentid is None:
                    raise NestedSetException('It is not valid to request a'
                        ' sibling update on the root node since only one root'
                        ' node is supported.')
                    
                if instance.upper_sibling:
                    log.debug('before_update: anchor is upper sibling')
                    if (ancredge + 1) == tuledge:
                        log.debug('before_update: anchor is already the upper'
                                  ' sibling, returning')
                        return
                    if tuledge > ancledge and turedge < ancredge:
                        """ upper sibling from child """    
                        log.debug('before_update: upper sibling from child')
                        left_bound_of_displaced  = turedge + 1
                        instance_children_shift = ancredge - turedge
                        right_bound_of_displaced = ancredge
                        displaced_shift = tuwidth * -1
                        right_boundary_for_ledge  = ancredge
                        left_boundary_for_redge = tuledge
                        
                        ancredgeaftershift = ancredge - tuwidth
                        instance.ledge = ancredgeaftershift + 1
                        instance.redge = instance.ledge + tuwidth - 1
                    elif tuledge > ancledge:
                        """ upper sibling from right"""
                        log.debug('before_update: upper sibling from right')
                        left_bound_of_displaced  = ancredge + 1
                        instance_children_shift = left_bound_of_displaced - tuledge
                        right_bound_of_displaced = tuledge-1
                        displaced_shift = turedge-tuledge+1
                        right_boundary_for_ledge  = turedge
                        left_boundary_for_redge = left_bound_of_displaced
                        
                        instance.ledge = ancredge + 1
                        instance.redge = ancredge + 1 + (turedge - tuledge)
                    else:
                        """ upper sibling from left """
                        log.debug('before_update: upper sibling from left')
                        left_bound_of_displaced  = turedge + 1
                        instance_children_shift = ancredge - tuledge + 1 - tuwidth
                        right_bound_of_displaced = ancredge
                        displaced_shift = tuwidth * -1
                        right_boundary_for_ledge  = ancledge+1
                        left_boundary_for_redge = tuledge
                        
                        instance.ledge = ancredge - (turedge - tuledge)
                        instance.redge = ancredge
                    
                else:
                    log.debug('before_update: anchor is lower sibling')
                    if (turedge+1) == ancledge:
                        log.debug('before_update: anchor is already the lower'
                                  ' sibling, returning')
                        return
                    if tuledge > ancledge:
                        """ lower sibling from right and from child """
                        log.debug('before_update: lower sibling from right and'
                                  ' from child')
                        left_bound_of_displaced  = ancledge
                        instance_children_shift = left_bound_of_displaced - tuledge
                        right_bound_of_displaced = tuledge-1
                        displaced_shift = turedge-tuledge+1
                        right_boundary_for_ledge  = turedge
                        left_boundary_for_redge = left_bound_of_displaced
                        
                        instance.ledge = ancledge
                        instance.redge = ancledge + (turedge - tuledge)
                    else:
                        """ lower sibling from left """
                        log.debug('before_update: lower sibling from left')
                        left_bound_of_displaced  = turedge + 1
                        instance_children_shift = ancledge - turedge -1
                        right_bound_of_displaced = ancledge - 1
                        displaced_shift = tuledge-turedge-1
                        right_boundary_for_ledge  = ancledge-1
                        left_boundary_for_redge = tuledge
                        
                        instance.ledge = ancledge - 1 - + (turedge - tuledge)
                        instance.redge = ancledge - 1 
                
                children_depth = ancdepth-tudepth
                instance.parentid = ancparentid
                instance.depth = ancdepth

            connection.execute(
                nodetbl.update() \
                    .where(
                        or_(
                            nodetbl.c.ledge < right_boundary_for_ledge,
                            nodetbl.c.redge > left_boundary_for_redge
                            )
                    ).values(
                        ledge = case(
                                [
                                    (nodetbl.c.ledge.between(left_bound_of_displaced,right_bound_of_displaced), nodetbl.c.ledge + displaced_shift),
                                    (nodetbl.c.ledge.between(tuledge,turedge), nodetbl.c.ledge + instance_children_shift)
                                ],
                                else_ = nodetbl.c.ledge
                              ),
                        redge = case(
                                [
                                    (nodetbl.c.redge.between(left_bound_of_displaced,right_bound_of_displaced), nodetbl.c.redge + displaced_shift),
                                    (nodetbl.c.redge.between(tuledge,turedge), nodetbl.c.redge + instance_children_shift)
                                ],
                                else_ = nodetbl.c.redge
                              ),
                        depth = case(
                                [(nodetbl.c.redge.between(tuledge,turedge), nodetbl.c.depth + children_depth)],
                                else_ = nodetbl.c.depth
                              ),
                    )
            )
        except:
            self._node_update_count -= 1
            raise

    def after_update(self, mapper, connection, instance):
        try:
            if self._node_update_count > 1:
                raise MultipleUpdatesError
        finally:
            self._node_update_count = 0

    def before_delete(self, mapper, connection, instance):
        self._node_delete_count += 1
        
    def after_delete(self, mapper, connection, instance):
        if self._node_delete_count > 1:
            raise MultipleDeletesError
        self._node_delete_count = 0
        
        nodetbl = mapper.mapped_table
        width = instance.redge - instance.ledge + 1
        
        # delete the node's children
        connection.execute(
            nodetbl.delete(
                and_(
                        nodetbl.c.ledge > instance.ledge,
                        nodetbl.c.ledge < instance.redge
                     )
            )
        )
        
        # close the gap
        connection.execute(
               nodetbl.update() \
                   .where(
                       nodetbl.c.redge > instance.ledge
                   ).values(
                       ledge = case(
                               [(nodetbl.c.ledge > instance.redge, nodetbl.c.ledge - width)],
                               else_ = nodetbl.c.ledge
                             ),
                       redge = nodetbl.c.redge - width
                   )
           )
class DeclarativeMixin(object):
    def to_dict(self, exclude=[]):
        col_prop_names = [p.key for p in self.__mapper__.iterate_properties \
                                      if isinstance(p, ColumnProperty)]
        data = dict([(name, getattr(self, name))
                     for name in col_prop_names if name not in exclude])
        return data
            
    # before_update() would be needed to support moving of nodes
    # after_delete() would be needed to support removal of nodes.
    # [ticket:1172] needs to be implemented for deletion to work as well.
    
#def node_base(bind=None, metadata=None, mapper=None, cls=object,
#                     name='Base', constructor=_declarative_constructor,
#                     metaclass=DeclarativeMeta, engine=None):
#    Base = declarative_base(bind, metadata, mapper, cls,
#                     name, constructor, metaclass, engine)
#
#    Base.__mapper_args__ = {
#        'extension':NestedSetExtension(), 
#        'batch':False  # allows extension to fire for each instance before going to the next.
#    }
#    
#    Base.parent = None
#    Base.upper_sibling = None
#    Base.lower_sibling = None
#    Base.ledge = Column("ledge", Integer, nullable=False)
#    Base.redge = Column("redge", Integer, nullable=False)
#    Base.parentid = Column("parentid", Integer)
#    Base.depth = Column("depth", Integer, nullable=False)
#
#    return Base

class SmallIntBool(sqlalchemy.types.TypeDecorator):
    # A SmallInteger type that always saves as 0 or 1 on the DB side and has
    # a True/False value on the Python side

    impl = sqlalchemy.types.SmallInteger

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return int(bool(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return bool(value)

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
    if use_dialect:
        relative_sql_path = 'modules/%s/sql/%s.%s.sql' % (module, target, db.engine.dialect.name )
    else:
        relative_sql_path = 'modules/%s/sql/%s.sql' % (module, target )
    _run_sql(relative_sql_path)

def run_app_sql(target, use_dialect=False):
    ''' used to run SQL from files in an apps "sql" directory:
    
            run_app_sql('test_setup')
        
        will run the file "<myapp>/sql/test_setup.sql"
        
            run_app_sql('test_setup', True)
        
        will run the files:
            
            # sqlite DB
            <myapp>/sql/test_setup.sqlite.sql
            # postgres DB
            <myapp>/sql/test_setup.pgsql.sql
            ...
        
        The dialect prefix used is the same as the sqlalchemy prefix.
        
        The SQL file can contain multiple statements.  They should be seperated
        with the text "--statement-break".
            
    '''
    if use_dialect:
        relative_sql_path = 'sql/%s.%s.sql' % (target, db.engine.dialect.name )
    else:
        relative_sql_path = 'sql/%s.sql' % target

    _run_sql(relative_sql_path)

def _run_sql(relative_sql_path):
    from pysmvt import appfilepath
    full_path = appfilepath(relative_sql_path)
    
    sqlfile = file(full_path)
    sql = sqlfile.read()
    sqlfile.close()
    try:
        for statement in sql.split('--statement-break'):
            statement.strip()
            if statement:
                db.sess.execute(statement)
        db.sess.commit()
    except Exception:
        db.sess.rollback()
        raise
@curry
def is_unique_exc(field_name, constraint_name, exc):
    if not isinstance(exc, IntegrityError):
        return False
    msg = str(exc)
    if db.engine.dialect.name == 'postgres':
        if 'unique' in msg and constraint_name in msg:
            return True
    elif db.engine.dialect.name == 'mssql':
        if 'unique index \'%s\'' % constraint_name in msg:
            return True
        if 'constraint \'%s\'' % constraint_name in msg:
            return True
    elif db.engine.dialect.name == 'sqlite':
        if ('column %s is not unique' % field_name in msg) or \
           ('columns %s are not unique' % ', '.join(field_name) in msg):
            return True
    return False

def clear_db():
    if db.engine.dialect.name == 'postgres':
        sql = []
        sql.append('DROP SCHEMA public cascade;')
        sql.append('CREATE SCHEMA public AUTHORIZATION %s;' % db.engine.url.username)
        sql.append('GRANT ALL ON SCHEMA public TO %s;' % db.engine.url.username)
        sql.append('GRANT ALL ON SCHEMA public TO public;')
        sql.append("COMMENT ON SCHEMA public IS 'standard public schema';")
        for exstr in sql:
            try:
                db.engine.execute(exstr)
            except Exception, e:
                print 'WARNING: %s' % e
    elif db.engine.dialect.name == 'sqlite':
        # drop the views
        sql = "select name from sqlite_master where type='view'"
        rows = db.engine.execute(sql)
        for row in rows:
            db.engine.execute('drop view %s' % row['name'])
        
        # drop the tables
        db.meta.reflect(bind=db.engine)
        for table in reversed(db.meta.sorted_tables):
            try:
                db.engine.execute(table.delete())
            except Exception, e:
                if not 'no such table' in str(e):
                    raise
    elif db.engine.dialect.name == 'mssql':
        mapping = {
            'P': 'drop procedure [%(name)s]',
            'C': 'alter table [%(parent_name)s] drop constraint [%(name)s]',
            ('FN', 'IF', 'TF'): 'drop function [%(name)s]',
            'V': 'drop view [%(name)s]',
            'F': 'alter table [%(parent_name)s] drop constraint [%(name)s]',
            'U': 'drop table [%(name)s]',
        }
        delete_sql = []
        to_repeat_sql = []
        for type, drop_sql in mapping.iteritems():
            sql = 'select name, object_name( parent_object_id ) as parent_name '\
                'from sys.objects where type in (\'%s\')' % '", "'.join(type)
            rows = db.engine.execute(sql)
            for row in rows:
                delete_sql.append(drop_sql % dict(row))
        for sql in delete_sql:
            db.engine.execute(sql)
    else:
        return False
    return True


@decorator
def dbtrans(f, *args, **kwargs):
    """
        decorates a function so that a DB transaction is always committed after
        the wrapped function returns and also rolls back the transaction if
        an unhandled exception occurs
    """
    try:
        retval = f(*args, **kwargs)
        db.sess.commit()
        return retval
    except Exception:
        db.sess.rollback()
        raise

@decorator
def sa_one_to_none(f, *args, **kwargs):
    """
        wraps a function that uses SQLAlahcemy's ORM .one() method and returns
        None instead of raising an exception if there was no record returned.
        If multiple records exist, that exception is still raised.
    """
    try:
        return f(*args, **kwargs)
    except NoResultFound, e:
        if 'No row was found for one()' != str(e):
            raise
        return None