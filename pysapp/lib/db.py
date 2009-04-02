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
    
class NestedSetExtension(MapperExtension):
    
    _nodes_getting_deleted = {}
    _node_delete_count = 0
    
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
                nparentid = ancnode.id
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

    def before_delete(self, mapper, connection, instance):
        self._node_delete_count += 1
        self._nodes_getting_deleted[getattr(instance, self.pkname)] = (instance.ledge, instance.redge)
            
    def after_delete(self, mapper, connection, instance):
        delete_and_shift = True
        for nid, nvalues in self._nodes_getting_deleted.items():
            if getattr(instance, self.pkname) != nid \
                and instance.ledge > nvalues[0] \
                and instance.ledge < nvalues[1]:
                delete_and_shift = False
                print "skipping %s because it is a child of %s" % (instance, nid)
        if delete_and_shift:
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