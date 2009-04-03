"""Celko's "Nested Sets" Tree Structure.

http://www.intelligententerprise.com/001020/celko.jhtml

"""

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm import attributes
from sqlalchemy.ext.declarative import declarative_base
from pysapp.lib.db import NestedSetExtension, MultipleRootsError, \
    MultipleAnchorsError, MultipleDeletesError, NestedSetException

engine = create_engine('sqlite://', echo=False)
Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'
    __mapper_args__ = {
        'extension':NestedSetExtension(), 
        'batch':False  # allows extension to fire for each instance before going to the next.
    }
    
    parent = None
    upper_sibling = None
    lower_sibling = None
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ledge = Column("ledge", Integer, nullable=False)
    redge = Column("redge", Integer, nullable=False)
    parentid = Column("parentid", Integer)
    _treeid = Column("treeid", Integer)
    depth = Column("depth", Integer, nullable=False)
    
    def gtreeid(self):
        return self._treeid or self.id
    def streeid(self, value):
        print value
        self._treeid = value
    treeid = property(gtreeid, streeid)
    
    def __repr__(self):
        return "Node(%s, %s, %s, %s, %s)" % (self.name, self.ledge, self.redge, self.parentid, self.depth)

def print_nodes():
    ealias = aliased(Node)
    for indentation, node in session.query(func.count(Node.id).label('indentation') - 1, ealias).\
        filter(ealias.ledge.between(Node.ledge, Node.redge)).\
        group_by(ealias.id).\
        order_by(ealias.ledge):
        print "    " * indentation + str(node)
        
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

# Node structure is based on graphic found here:
#http://dev.mysql.com/tech-resources/articles/hierarchical-data.html

class TestOrderedInsert(object):
    
    @classmethod
    def setup_class(cls):
        session.execute('DELETE FROM nodes')
        session.commit()
        electronics = Node(name='Electronics')
        tvs = Node(name='Televisions')
        pes = Node(name='Portable Electronics')
        tube = Node(name='Tube')
        lcd = Node(name='LCD')
        plasma = Node(name='Plasma')
        mp3p = Node(name='MP3 Players')
        cdp = Node(name='CD Players')
        tway = Node(name='2-Way Radios')
        flash = Node(name='Flash')
        
        tvs.parent = electronics
        pes.parent = electronics
        tube.parent = tvs
        lcd.parent = tvs
        plasma.parent = tvs
        mp3p.parent = pes
        cdp.parent = pes
        tway.parent = pes
        flash.parent = mp3p
        
        # the order of "add" is important here.  elements must be added in
        # the order in which they should be INSERTed.
        session.add_all([electronics, tvs, pes, tube, lcd, plasma, mp3p, cdp, tway, flash])
        #session.add_all([electronics, tvs])
        session.commit()

    def test_electronics(self):
        el = session.query(Node).filter_by(name='Electronics').one()
        assert el.ledge == 1
        assert el.redge == 20
        assert el.parentid is None
        assert el.depth == 1

    def test_tvs(self):
        el = session.query(Node).filter_by(name='Televisions').one()
        assert el.ledge == 2
        assert el.redge == 9
        assert el.parentid == 1
        assert el.depth == 2

    def test_tube(self):
        el = session.query(Node).filter_by(name='Tube').one()
        assert el.ledge == 3
        assert el.redge == 4
        assert el.parentid == 2 
        assert el.depth == 3

    def test_lcd(self):
        el = session.query(Node).filter_by(name='LCD').one()
        assert el.ledge == 5
        assert el.redge == 6
        assert el.parentid == 2 
        assert el.depth == 3

    def test_plasma(self):
        el = session.query(Node).filter_by(name='Plasma').one()
        assert el.ledge == 7
        assert el.redge == 8
        assert el.parentid == 2 
        assert el.depth == 3

    def test_pes(self):
        el = session.query(Node).filter_by(name='Portable Electronics').one()
        assert el.ledge == 10
        assert el.redge == 19
        assert el.parentid == 1
        assert el.depth == 2

    def test_mp3p(self):
        el = session.query(Node).filter_by(name='MP3 Players').one()
        assert el.ledge == 11
        assert el.redge == 14
        assert el.parentid == 3
        assert el.depth == 3

    def test_cdp(self):
        el = session.query(Node).filter_by(name='CD Players').one()
        assert el.ledge == 15
        assert el.redge == 16
        assert el.parentid == 3
        assert el.depth == 3

    def test_tway(self):
        el = session.query(Node).filter_by(name='2-Way Radios').one()
        assert el.ledge == 17
        assert el.redge == 18
        assert el.parentid == 3
        assert el.depth == 3

    def test_flash(self):
        el = session.query(Node).filter_by(name='Flash').one()
        assert el.ledge == 12
        assert el.redge == 13
        assert el.parentid == 7
        assert el.depth == 4

class TestSiblingInsert(object):
    
    @classmethod
    def setup_class(cls):
        session.execute('DELETE FROM nodes')
        session.commit()
        electronics = Node(name='Electronics')
        tvs = Node(name='Televisions')
        pes = Node(name='Portable Electronics')
        tube = Node(name='Tube')
        lcd = Node(name='LCD')
        plasma = Node(name='Plasma')
        mp3p = Node(name='MP3 Players')
        cdp = Node(name='CD Players')
        tway = Node(name='2-Way Radios')
        flash = Node(name='Flash')
        
        tvs.parent = electronics
        pes.parent = electronics
        tube.parent = tvs
        plasma.parent = tvs
        lcd.upper_sibling = tube
        mp3p.parent = pes
        tway.parent = pes
        cdp.lower_sibling = tway
        flash.parent = mp3p
        
        # the order of "add" is important here.  elements must be added in
        # the order in which they should be INSERTed.
        session.add_all([electronics, tvs, pes, tube, plasma, lcd, mp3p, tway, cdp, flash])
        #session.add_all([electronics, tvs])
        session.commit()

    def test_electronics(self):
        el = session.query(Node).filter_by(name='Electronics').one()
        assert el.ledge == 1
        assert el.redge == 20
        assert el.parentid is None
        assert el.depth == 1

    def test_tvs(self):
        el = session.query(Node).filter_by(name='Televisions').one()
        assert el.ledge == 2
        assert el.redge == 9
        assert el.parentid == 1
        assert el.depth == 2

    def test_tube(self):
        el = session.query(Node).filter_by(name='Tube').one()
        assert el.ledge == 3
        assert el.redge == 4
        assert el.parentid == 2 
        assert el.depth == 3

    def test_lcd(self):
        el = session.query(Node).filter_by(name='LCD').one()
        assert el.ledge == 5
        assert el.redge == 6
        assert el.parentid == 2 
        assert el.depth == 3

    def test_plasma(self):
        el = session.query(Node).filter_by(name='Plasma').one()
        assert el.ledge == 7
        assert el.redge == 8
        assert el.parentid == 2 
        assert el.depth == 3

    def test_pes(self):
        el = session.query(Node).filter_by(name='Portable Electronics').one()
        assert el.ledge == 10
        assert el.redge == 19
        assert el.parentid == 1
        assert el.depth == 2

    def test_mp3p(self):
        el = session.query(Node).filter_by(name='MP3 Players').one()
        assert el.ledge == 11
        assert el.redge == 14
        assert el.parentid == 3
        assert el.depth == 3

    def test_cdp(self):
        el = session.query(Node).filter_by(name='CD Players').one()
        assert el.ledge == 15
        assert el.redge == 16
        assert el.parentid == 3
        assert el.depth == 3

    def test_tway(self):
        el = session.query(Node).filter_by(name='2-Way Radios').one()
        assert el.ledge == 17
        assert el.redge == 18
        assert el.parentid == 3
        assert el.depth == 3

    def test_flash(self):
        el = session.query(Node).filter_by(name='Flash').one()
        assert el.ledge == 12
        assert el.redge == 13
        assert el.parentid == 7
        assert el.depth == 4

class TestExceptions(object):
    
    @classmethod
    def setup_class(cls):
        session.execute('DELETE FROM nodes')
        session.commit()

    def test_multiple_roots(self):
        r1 = Node(name='Root1')
        r2 = Node(name='Root2')
        try:
            session.add_all([r1, r2])
            session.commit()
            assert False, 'Should have got an exception for multiple roots'
        except MultipleRootsError:
            session.rollback()

    def test_multiple_anchors(self):
        r1 = Node(name='Root1')
        c1 = Node(name='Child1')
        c2 = Node(name='Child2')
        
        c1.parent = r1
        c2.parent = r1
        c2.upper_sibling = c1
        
        try:
            session.add_all([r1, c1, c2])
            session.commit()
            assert False, 'Should have got an exception for multiple anchors'
        except MultipleAnchorsError:
            session.rollback()

class TestDelete(object):
    
    def setUp(self):
        session.execute('DELETE FROM nodes')
        session.commit()
        electronics = Node(name='Electronics')
        tvs = Node(name='Televisions')
        pes = Node(name='Portable Electronics')
        tube = Node(name='Tube')
        lcd = Node(name='LCD')
        plasma = Node(name='Plasma')
        mp3p = Node(name='MP3 Players')
        cdp = Node(name='CD Players')
        tway = Node(name='2-Way Radios')
        flash = Node(name='Flash')
        
        tvs.parent = electronics
        pes.parent = electronics
        tube.parent = tvs
        plasma.parent = tvs
        lcd.upper_sibling = tube
        mp3p.parent = pes
        tway.parent = pes
        cdp.lower_sibling = tway
        flash.parent = mp3p
        
        # the order of "add" is important here.  elements must be added in
        # the order in which they should be INSERTed.
        session.add_all([electronics, tvs, pes, tube, plasma, lcd, mp3p, tway, cdp, flash])
        #session.add_all([electronics, tvs])
        session.commit()
    
    def test_delete1(self):
        el = session.query(Node).filter_by(name='MP3 Players').one()
        session.delete(el)
        session.commit()
        
        el = session.query(Node).filter_by(name='Electronics').one()
        assert el.ledge == 1
        assert el.redge == 16
        assert el.parentid is None
        assert el.depth == 1
        el = session.query(Node).filter_by(name='Televisions').one()
        assert el.ledge == 2
        assert el.redge == 9
        assert el.parentid == 1
        assert el.depth == 2
        el = session.query(Node).filter_by(name='Tube').one()
        assert el.ledge == 3
        assert el.redge == 4
        assert el.parentid == 2 
        assert el.depth == 3
        el = session.query(Node).filter_by(name='LCD').one()
        assert el.ledge == 5
        assert el.redge == 6
        assert el.parentid == 2 
        assert el.depth == 3
        el = session.query(Node).filter_by(name='Plasma').one()
        assert el.ledge == 7
        assert el.redge == 8
        assert el.parentid == 2 
        assert el.depth == 3
        el = session.query(Node).filter_by(name='Portable Electronics').one()
        assert el.ledge == 10
        assert el.redge == 15
        assert el.parentid == 1
        assert el.depth == 2
        el = session.query(Node).filter_by(name='CD Players').one()
        assert el.ledge == 11
        assert el.redge == 12
        assert el.parentid == 3
        assert el.depth == 3
        el = session.query(Node).filter_by(name='2-Way Radios').one()
        assert el.ledge == 13
        assert el.redge == 14
        assert el.parentid == 3
        assert el.depth == 3
    
    def test_delete2(self):
        el = session.query(Node).filter_by(name='MP3 Players').one()
        session.delete(el)
        el = session.query(Node).filter_by(name='Televisions').one()
        session.delete(el)
        session.commit()
        
        el = session.query(Node).filter_by(name='Electronics').one()
        assert el.ledge == 1
        assert el.redge == 8
        assert el.parentid is None
        assert el.depth == 1
        el = session.query(Node).filter_by(name='Portable Electronics').one()
        assert el.ledge == 2
        assert el.redge == 7
        assert el.parentid == 1
        assert el.depth == 2
        el = session.query(Node).filter_by(name='CD Players').one()
        assert el.ledge == 3
        assert el.redge == 4
        assert el.parentid == 3
        assert el.depth == 3
        el = session.query(Node).filter_by(name='2-Way Radios').one()
        assert el.ledge == 5
        assert el.redge == 6
        assert el.parentid == 3
        assert el.depth == 3
        
    def test_delete_parent_then_child(self):
        tv = session.query(Node).filter_by(name='Televisions').one()
        lcd = session.query(Node).filter_by(name='LCD').one()
        session.delete(lcd)
        session.commit()
        session.delete(tv)
        session.commit()

        el = session.query(Node).filter_by(name='Electronics').one()
        assert el.ledge == 1
        assert el.redge == 12
        assert el.parentid is None
        assert el.depth == 1
        el = session.query(Node).filter_by(name='Portable Electronics').one()
        assert el.ledge == 2
        assert el.redge == 11
        assert el.parentid == 1
        assert el.depth == 2
        el = session.query(Node).filter_by(name='CD Players').one()
        assert el.ledge == 7
        assert el.redge == 8
        assert el.parentid == 3
        assert el.depth == 3
        el = session.query(Node).filter_by(name='2-Way Radios').one()
        assert el.ledge == 9
        assert el.redge == 10
        assert el.parentid == 3
        assert el.depth == 3
        el = session.query(Node).filter_by(name='MP3 Players').one()
        assert el.ledge == 3
        assert el.redge == 6
        assert el.parentid == 3
        assert el.depth == 3
        el = session.query(Node).filter_by(name='Flash').one()
        assert el.ledge == 4
        assert el.redge == 5
        assert el.parentid == 7
        assert el.depth == 4
    
    def test_multiple_delets(self):
        tv = session.query(Node).filter_by(name='Televisions').one()
        lcd = session.query(Node).filter_by(name='LCD').one()
        session.delete(lcd)
        session.delete(tv)
        try:
            session.commit()
            assert False, 'should have got an exception for multiple deletes'
        except MultipleDeletesError:
            session.rollback()
        
    #def test_delete_ptc_not_child(self):
    #    """
    #    Delete a node and a non-child node
    #    """
    #    
    #    tv = session.query(Node).filter_by(name='Televisions').one()
    #    #lcd = session.query(Node).filter_by(name='LCD').one()
    #    mp3 = session.query(Node).filter_by(name='MP3 Players').one()
    #    session.delete(mp3)
    #    session.delete(tv)
    #    try:
    #        session.commit()
    #    except:
    #        session.rollback()
    #        raise
    #    print_nodes()
    #    el = session.query(Node).filter_by(name='Electronics').one()
    #    assert el.ledge == 1
    #    assert el.redge == 8
    #    assert el.parentid is None
    #    assert el.depth == 1
    #    el = session.query(Node).filter_by(name='Portable Electronics').one()
    #    assert el.ledge == 2
    #    assert el.redge == 7
    #    assert el.parentid == 1
    #    assert el.depth == 2
    #    el = session.query(Node).filter_by(name='CD Players').one()
    #    assert el.ledge == 3
    #    assert el.redge == 4
    #    assert el.parentid == 3
    #    assert el.depth == 3
    #    el = session.query(Node).filter_by(name='2-Way Radios').one()
    #    assert el.ledge == 5
    #    assert el.redge == 6
    #    assert el.parentid == 3
    #    assert el.depth == 3
    
class TestUpdate(object):
    
    def setUp(self):
        session.rollback()
        session.execute('DELETE FROM nodes')
        session.commit()
        electronics = Node(name='Electronics')
        tvs = Node(name='Televisions')
        pes = Node(name='Portable Electronics')
        tube = Node(name='Tube')
        lcd = Node(name='LCD')
        plasma = Node(name='Plasma')
        mp3p = Node(name='MP3 Players')
        cdp = Node(name='CD Players')
        tway = Node(name='2-Way Radios')
        flash = Node(name='Flash')
        
        tvs.parent = electronics
        pes.parent = electronics
        tube.parent = tvs
        plasma.parent = tvs
        lcd.upper_sibling = tube
        mp3p.parent = pes
        tway.parent = pes
        cdp.lower_sibling = tway
        flash.parent = mp3p
        
        # the order of "add" is important here.  elements must be added in
        # the order in which they should be INSERTed.
        session.add_all([electronics, tvs, pes, tube, plasma, lcd, mp3p, tway, cdp, flash])
        #session.add_all([electronics, tvs])
        session.commit()
    
    # We can apparently do multiple udpates, not sure why delete gives us a problem.
    #def test_multiple_error(self):
    #    plasma = session.query(Node).filter_by(name='Plasma').one()
    #    lcd = session.query(Node).filter_by(name='LCD').one()
    #    lcd.upper_sibling = plasma
    #    # required to make the object "dirty" so that the update will work
    #    lcd.name = lcd.name
    #    plasma.name = "test"
    #    session.commit()
    
    # We can apparently do multiple udpates, not sure why delete gives us a problem.
    def test_multiple_anchors(self):
        plasma = session.query(Node).filter_by(name='Plasma').one()
        lcd = session.query(Node).filter_by(name='LCD').one()
        mp3p = session.query(Node).filter_by(name='MP3 Players').one()
        lcd.upper_sibling = plasma
        lcd.parent = mp3p
        # required to make the object "dirty" so that the update will work
        lcd.name = lcd.name
        try:
            session.commit()
            assert False, 'should have got a multiple anchors exception'
        except MultipleAnchorsError:
            session.rollback()
    
    def test_no_anchor(self):
        lcd = session.query(Node).filter_by(name='LCD').one()
        # required to make the object "dirty" so that the update will work
        lcd.name = lcd.name
        session.commit()
        check_for_no_updates()
    
    def test_self_anchor(self):
        lcd = session.query(Node).filter_by(name='LCD').one()
        # required to make the object "dirty" so that the update will work
        lcd.name = lcd.name
        lcd.parent = lcd
        try:
            session.commit()
            assert False, 'should have got self anchor exception'
        except Exception, e:
            session.rollback()
            if 'A nodes anchor can not be iteself.' != str(e):
                raise
        check_for_no_updates()
    
    def test_child_anchor(self):
        tvs = session.query(Node).filter_by(name='Televisions').one()
        lcd = session.query(Node).filter_by(name='LCD').one()
        # required to make the object "dirty" so that the update will work
        tvs.name = tvs.name
        tvs.lower_sibling = lcd
        try:
            session.commit()
            assert False, 'should have got child anchor exception'
        except Exception, e:
            session.rollback()
            if 'A nodes anchor can not be one of its children.' != str(e):
                raise
        check_for_no_updates()
    
    def test_already_anchored_parent(self):
        tvs = session.query(Node).filter_by(name='Televisions').one()
        lcd = session.query(Node).filter_by(name='LCD').one()
        # required to make the object "dirty" so that the update will work
        lcd.name = lcd.name
        lcd.parent = tvs
        session.commit()
        check_for_no_updates()
    
    def test_already_anchored_us(self):    
        tube = session.query(Node).filter_by(name='Tube').one()
        lcd = session.query(Node).filter_by(name='LCD').one()
        # required to make the object "dirty" so that the update will work
        lcd.name = lcd.name
        lcd.upper_sibling = tube
        session.commit()
        check_for_no_updates()
    
    def test_already_anchored_ls(self):    
        plasma = session.query(Node).filter_by(name='Plasma').one()
        lcd = session.query(Node).filter_by(name='LCD').one()
        # required to make the object "dirty" so that the update will work
        lcd.name = lcd.name
        lcd.lower_sibling = plasma
        session.commit()
        check_for_no_updates()
    
    def test_parent_update_1(self):
        elc = session.query(Node).filter_by(name='Electronics').one()
        tube = session.query(Node).filter_by(name='Tube').one()
        # required to make the object "dirty" so that the update will work
        tube.name = tube.name
        tube.parent = elc
        session.commit()
        
        el = session.query(Node).filter_by(name='Electronics').one()
        assert el.ledge == 1
        assert el.redge == 20
        assert el.parentid is None
        assert el.depth == 1
        el = session.query(Node).filter_by(name='Tube').one()
        assert el.ledge == 2
        assert el.redge == 3
        assert el.parentid == 1
        assert el.depth == 2
        el = session.query(Node).filter_by(name='Televisions').one()
        assert el.ledge == 4
        assert el.redge == 9
        assert el.parentid == 1
        assert el.depth == 2
        el = session.query(Node).filter_by(name='LCD').one()
        assert el.ledge == 5
        assert el.redge == 6
        assert el.parentid == 2 
        assert el.depth == 3
        el = session.query(Node).filter_by(name='Plasma').one()
        assert el.ledge == 7
        assert el.redge == 8
        assert el.parentid == 2 
        assert el.depth == 3
        el = session.query(Node).filter_by(name='Portable Electronics').one()
        assert el.ledge == 10
        assert el.redge == 19
        assert el.parentid == 1
        assert el.depth == 2
        el = session.query(Node).filter_by(name='CD Players').one()
        assert el.ledge == 15
        assert el.redge == 16
        assert el.parentid == 3
        assert el.depth == 3
        el = session.query(Node).filter_by(name='2-Way Radios').one()
        assert el.ledge == 17
        assert el.redge == 18
        assert el.parentid == 3
        assert el.depth == 3
        el = session.query(Node).filter_by(name='MP3 Players').one()
        assert el.ledge == 11
        assert el.redge == 14
        assert el.parentid == 3
        assert el.depth == 3
        el = session.query(Node).filter_by(name='Flash').one()
        assert el.ledge == 12
        assert el.redge == 13
        assert el.parentid == 7
        assert el.depth == 4
    
    def test_parent_update_2(self):
        pes = session.query(Node).filter_by(name='Portable Electronics').one()
        lcds = session.query(Node).filter_by(name='LCD').one()
        # required to make the object "dirty" so that the update will work
        pes.name = pes.name
        pes.parent = lcds
        session.commit()
        
        el = session.query(Node).filter_by(name='Electronics').one()
        assert el.ledge == 1
        assert el.redge == 20
        assert el.parentid is None
        assert el.depth == 1
        el = session.query(Node).filter_by(name='Televisions').one()
        assert el.ledge == 2
        assert el.redge == 19
        assert el.parentid == 1
        assert el.depth == 2
        el = session.query(Node).filter_by(name='Tube').one()
        assert el.ledge == 3
        assert el.redge == 4
        assert el.parentid == 2 
        assert el.depth == 3
        el = session.query(Node).filter_by(name='LCD').one()
        assert el.ledge == 5
        assert el.redge == 16
        assert el.parentid == 2 
        assert el.depth == 3
        el = session.query(Node).filter_by(name='Plasma').one()
        assert el.ledge == 17
        assert el.redge == 18
        assert el.parentid == 2 
        assert el.depth == 3
        el = session.query(Node).filter_by(name='Portable Electronics').one()
        assert el.ledge == 6
        assert el.redge == 15
        assert el.parentid == 6
        assert el.depth == 4
        el = session.query(Node).filter_by(name='MP3 Players').one()
        assert el.ledge == 7
        assert el.redge == 10
        assert el.parentid == 3
        assert el.depth == 5
        el = session.query(Node).filter_by(name='Flash').one()
        assert el.ledge == 8
        assert el.redge == 9
        assert el.parentid == 7
        assert el.depth == 6
        el = session.query(Node).filter_by(name='CD Players').one()
        assert el.ledge == 11
        assert el.redge == 12
        assert el.parentid == 3
        assert el.depth == 5
        el = session.query(Node).filter_by(name='2-Way Radios').one()
        assert el.ledge == 13
        assert el.redge == 14
        assert el.parentid == 3
        assert el.depth == 5
        
        # move portable electronics back, but it will be at the front now
        elc = session.query(Node).filter_by(name='Electronics').one()
        pes.parent = elc
        pes.name = pes.name
        session.commit()
        
        # move TVs to somewhere else and then back, so that its first
        tvs = session.query(Node).filter_by(name='Televisions').one()
        tvs.parent = pes
        tvs.name = tvs.name
        session.commit()
        
        assert tvs.ledge == 3
        assert tvs.redge == 10
        assert tvs.parentid == 3
        assert tvs.depth == 3
        
        tvs.name = tvs.name
        tvs.parent = elc
        session.commit()
        
        check_for_no_updates()
        
    def test_siblings(self):
        plasma = session.query(Node).filter_by(name='Plasma').one()
        lcd = session.query(Node).filter_by(name='LCD').one()
        lcd.upper_sibling = plasma
        # required to make the object "dirty" so that the update will work
        #lcd.name = lcd.name
        #session.commit()
        check_for_no_updates()
        
def check_for_no_updates():       
    el = session.query(Node).filter_by(name='Electronics').one()
    assert el.ledge == 1
    assert el.redge == 20
    assert el.parentid is None
    assert el.depth == 1
    el = session.query(Node).filter_by(name='Televisions').one()
    assert el.ledge == 2
    assert el.redge == 9
    assert el.parentid == 1
    assert el.depth == 2
    el = session.query(Node).filter_by(name='Tube').one()
    assert el.ledge == 3
    assert el.redge == 4
    assert el.parentid == 2 
    assert el.depth == 3
    el = session.query(Node).filter_by(name='LCD').one()
    assert el.ledge == 5
    assert el.redge == 6
    assert el.parentid == 2 
    assert el.depth == 3
    el = session.query(Node).filter_by(name='Plasma').one()
    assert el.ledge == 7
    assert el.redge == 8
    assert el.parentid == 2 
    assert el.depth == 3
    el = session.query(Node).filter_by(name='Portable Electronics').one()
    assert el.ledge == 10
    assert el.redge == 19
    assert el.parentid == 1
    assert el.depth == 2
    el = session.query(Node).filter_by(name='CD Players').one()
    assert el.ledge == 15
    assert el.redge == 16
    assert el.parentid == 3
    assert el.depth == 3
    el = session.query(Node).filter_by(name='2-Way Radios').one()
    assert el.ledge == 17
    assert el.redge == 18
    assert el.parentid == 3
    assert el.depth == 3
    el = session.query(Node).filter_by(name='MP3 Players').one()
    assert el.ledge == 11
    assert el.redge == 14
    assert el.parentid == 3
    assert el.depth == 3
    el = session.query(Node).filter_by(name='Flash').one()
    assert el.ledge == 12
    assert el.redge == 13
    assert el.parentid == 7
    assert el.depth == 4