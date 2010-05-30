from werkzeug import create_environ
from werkzeug.exceptions import BadRequest
from pysmvt import db
from pysmvt.routing import current_url
from pysmvt.utils import wrapinapp
from _supporting import Person, assertEqualSQL
from sqlalchemy.sql import select
from pysmvt.htmltable import Col
from pysapp.modules.datagrid.utils import DataGrid

class TestQueryBuilding(object):
    
    def test_resultset_columns(self):
        environ = create_environ('/foo', 'http://localhost')
        tbl = Person.__table__
        p = DataGrid(Person,
            environ = environ)
        p.add_col(
            'Id',
            Person.id,
            inresult=True
        )
        p.add_tablecol(
            Col('First Name'),
            tbl.c.firstname
            )
        p.add_tablecol(
            Col('Last Name'),
            Person.lastname
        )
        p.add_col(
            'Sort Order',
            Person.sortorder,
        )
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons"""
        assertEqualSQL( str(p.get_query()), sql)

    def test_ordering(self):
        environ = create_environ('/foo', 'http://localhost')
        tbl = Person.__table__
        p = DataGrid(
            Person,
            lambda q: q.order_by(Person.lastname, Person.firstname),
            lambda q: q.where(Person.createdts >= '2009-01-01'),
            lambda q: q.where(Person.inactive == 0),
            environ = environ
            )
        p.add_col(
            'Id',
            Person.id,
            inresult=True
        )
        p.add_tablecol(
            Col('First Name'),
            tbl.c.firstname
            )
        p.add_tablecol(
            Col('Last Name'),
            Person.lastname
        )
        p.add_col(
            'Sort Order',
            Person.sortorder,
        )
        
        p.add_sort('inactive state DESC', Person.inactive, Person.state.desc())
        p.add_sort('inactive state ASC', Person.inactive, Person.state)
        
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.createdts >= :createdts_1 AND persons.inactive = :inactive_1 ORDER BY persons.last_name, persons.firstname"""
        assertEqualSQL( str(p.get_query()), sql)
        
        ### header sorting
        p._replace_environ(create_environ('/foo?sort=firstname', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.createdts >= :createdts_1 AND persons.inactive = :inactive_1 ORDER BY persons.firstname"""
        assertEqualSQL( str(p.get_query()), sql)
        
        ### header sorting desc
        p._replace_environ(create_environ('/foo?sort=-firstname', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.createdts >= :createdts_1 AND persons.inactive = :inactive_1 ORDER BY persons.firstname DESC"""
        assertEqualSQL( str(p.get_query()), sql)
        
        ### header sorting, duplicate entries are just like a single entry
        p._replace_environ(create_environ('/foo?sort=firstname&sort=lastname', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.createdts >= :createdts_1 AND persons.inactive = :inactive_1 ORDER BY persons.firstname"""
        assertEqualSQL( str(p.get_query()), sql)
        
        ### header sorting for invalid column
        p._replace_environ(create_environ('/foo?sort=notthere', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### header sorting for non-header column
        p._replace_environ(create_environ('/foo?sort=id', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
    
        ### drop-down box sorting
        p._replace_environ(create_environ('/foo?sortdd=inactivestateasc', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.createdts >= :createdts_1 AND persons.inactive = :inactive_1 ORDER BY persons.inactive, persons.state"""
        assertEqualSQL( str(p.get_query()), sql)
        
        ### drop-down box sorting takes precidence over heading sorting
        p._replace_environ(create_environ('/foo?sort=firstname&sortdd=inactivestateasc', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.createdts >= :createdts_1 AND persons.inactive = :inactive_1 ORDER BY persons.inactive, persons.state"""
        assertEqualSQL( str(p.get_query()), sql)
        
        ### drop-down invalid
        p._replace_environ(create_environ('/foo?sortdd=nothere', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass

    def test_paging(self):
        environ = create_environ('/foo', 'http://localhost')
        tbl = Person.__table__
        p = DataGrid(
            Person,
            per_page = 20,
            environ = environ
            )
        p.add_col(
            'Id',
            Person.id,
            inresult=True
        )
        p.add_tablecol(
            Col('First Name'),
            tbl.c.firstname
            )
        p.add_tablecol(
            Col('Last Name'),
            Person.lastname
        )
        p.add_col(
            'Sort Order',
            Person.sortorder,
        )
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
 LIMIT 20 OFFSET 0"""
        assertEqualSQL( str(p.get_query()), sql)
        
        ### non-int perpage
        p._replace_environ(create_environ('/foo?perpage=test', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### <1 perpage
        p._replace_environ(create_environ('/foo?perpage=-1', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### <1 page
        p._replace_environ(create_environ('/foo?page=-1', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### non-int page
        p._replace_environ(create_environ('/foo?page=test', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        # the rest of these tests need a "count" to work, but we aren't working
        # with any data currenty, so we are going to fake it
        p._count = 100
        
        # user page size
        p._replace_environ(create_environ('/foo?perpage=30&page=1', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
 LIMIT 30 OFFSET 0"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # user page size > number of pages = max page (4)
        p._replace_environ(create_environ('/foo?perpage=30&page=100', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
 LIMIT 30 OFFSET 90"""
        assertEqualSQL( str(p.get_query()), sql)

    def test_filtering(self):
        environ = create_environ('/foo', 'http://localhost')
        tbl = Person.__table__
        p = DataGrid(
            Person,
            None,
            lambda q: q.where(Person.createdts >= '2009-01-01'),
            lambda q: q.where(Person.inactive == 0),
            environ = environ
            )
        p.add_col(
            'Id',
            Person.id,
            inresult=True
        )
        p.add_tablecol(
            Col('First Name'),
            tbl.c.firstname,
            filter_on=True
            )
        p.add_tablecol(
            Col('Last Name'),
            Person.lastname,
            filter_on=True
        )
        p.add_col(
            'Sort Order',
            Person.sortorder,
        )
        p.add_col(
            'createdts',
            Person.createdts,
            filter_on=True
        )
        p.add_col(
            'floatcol',
            Person.floatcol,
            filter_on=True
        )
        p.add_col(
            'numericcol',
            Person.numericcol,
            filter_on=True
        )
        p.add_col(
            'boolcol',
            Person.boolcol,
            filter_on=True
        )
        
        # permanent filter and default filter
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.createdts >= :createdts_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        ### invalid ident
        p._replace_environ(create_environ('/foo?filteron=nothere', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### column not in filter
        p._replace_environ(create_environ('/foo?filteron=sortorder', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### no operator
        p._replace_environ(create_environ('/foo?filteron=firstname', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### no "for"
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=lt', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### bad operator
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=foo&filterfor=test', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### wildcards in < test
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=lt&filterfor=*test', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### null in < test
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=lt&filterfor=', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### non-int value for integer
        p._replace_environ(create_environ('/foo?filteron=sortorder&filteronop=lt&filterfor=foo', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### non-float value for float
        p._replace_environ(create_environ('/foo?filteron=floatcol&filteronop=lt&filterfor=foo', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        ### non-decimal value for decimal
        p._replace_environ(create_environ('/foo?filteron=numericcol&filteronop=lt&filterfor=foo', 'http://localhost'))
        try:
            p.get_query()
            assert False, 'should have got a BadRequest exception'
        except BadRequest:
            pass
        
        # < filter
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=lt&filterfor=5', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.firstname < :firstname_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # > filter
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=gt&filterfor=5', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.firstname > :firstname_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # >= filter
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=gte&filterfor=5', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.firstname >= :firstname_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # <= filter
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=lte&filterfor=5', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.firstname <= :firstname_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # == filter
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=eq&filterfor=5', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.firstname = :firstname_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # != filter
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=ne&filterfor=5', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.firstname != :firstname_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # LIKE filter
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=eq&filterfor=test*', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.firstname LIKE :firstname_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # != filter
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=ne&filterfor=test*', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.firstname NOT LIKE :firstname_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # timestamp filter
        p._replace_environ(create_environ('/foo?filteron=createdts&filteronop=eq&filterfor=10%2F26%2F2009', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.createdts = :createdts_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
        
        # empty timestamp filter
        p._replace_environ(create_environ('/foo?filteron=createdts&filteronop=eq&filterfor=', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.createdts IS NULL AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)

        # contains filter
        p._replace_environ(create_environ('/foo?filteron=firstname&filteronop=contains&filterfor=test', 'http://localhost'))
        sql = """SELECT persons.id AS persons_id, persons.firstname AS persons_firstname, persons.last_name AS persons_last_name 
FROM persons 
WHERE persons.firstname LIKE :firstname_1 AND persons.inactive = :inactive_1"""
        assertEqualSQL( str(p.get_query()), sql)
