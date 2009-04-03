from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base, \
    DeclarativeMeta, _declarative_constructor

__all__ = [
    'NestedSetExtension'
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
                # if the nodes parent is already the requested parent, do nothing
                if tuparentid == getattr(anchor, self.pkname):
                    return
                if tuledge > ancledge:
                    treeshift  = ancledge - tuledge + 1;
                    leftbound  = ancledge+1;
                    rightbound = tuledge-1;
                    tuwidth     = turedge-tuledge+1;
                    leftrange  = turedge;
                    rightrange = ancledge;
                else:
                    treeshift  = ancledge - turedge;
                    leftbound  = turedge + 1;
                    rightbound = ancledge;
                    tuwidth     = tuledge-turedge-1;
                    leftrange  = ancledge+1;
                    rightrange = tuledge;
                
                instance.parentid = getattr(anchor, self.pkname)
                instance.ledge = ancledge + 1 
                instance.redge = ancledge + 1 + (turedge - tuledge)
                instance.depth = ancdepth + 1
            else:
                if instance.upper_sibling:
                    if (ancredge + 1) == tuledge:
                        # anchor is already the upper sibling
                        return
                else:
                    if (turedge+1) == ancledge:
                        # anchor is already lower sibling
                        return

            connection.execute(
                nodetbl.update() \
                    .where(
                        or_(
                            nodetbl.c.ledge < leftrange,
                            nodetbl.c.redge > rightrange
                            )
                    ).values(
                        ledge = case(
                                [
                                    (nodetbl.c.ledge.between(leftbound,rightbound), nodetbl.c.ledge + tuwidth),
                                    (nodetbl.c.ledge.between(tuledge,turedge), nodetbl.c.ledge + treeshift)
                                ],
                                else_ = nodetbl.c.ledge
                              ),
                        redge = case(
                                [
                                    (nodetbl.c.redge.between(leftbound,rightbound), nodetbl.c.redge + tuwidth),
                                    (nodetbl.c.redge.between(tuledge,turedge), nodetbl.c.redge + treeshift)
                                ],
                                else_ = nodetbl.c.redge
                              ),
                        depth = case(
                                [(nodetbl.c.redge.between(tuledge,turedge), nodetbl.c.depth + (ancdepth-tudepth+1))],
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