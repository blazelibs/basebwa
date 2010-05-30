from werkzeug import create_environ
from pysmvt import db
from pysmvt.routing import current_url
from pysmvt.utils import wrapinapp
from _supporting import Person, assertEqualSQL
from sqlalchemy.sql import select
from pysmvt.htmltable import Col, YesNo
from pysapp.modules.datagrid.utils import DataGrid, DataColumn, TableColumn

class TestQueryBuilding(object):
    
    def test_ident_creation(self):
        tbl = Person.__table__
        p = DataGrid(Person)
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
        ),
        p.add_col(
            'Sort Order',
            Person.sortorder,
        )
        assert p.data_cols.keys() == ['id', 'firstname', 'lastname', 'sortorder', 'sortorder2'], p.data_cols.keys()
    
    def test_sortdd(self):
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
            Person.lastname,
            sort='both'
        )
        p.add_tablecol(
            YesNo('Inactive'),
            Person.inactive,
            sort='drop-down'
        )
        p.add_col(
            'Sort Order',
            Person.sortorder,
        )
        
        p.add_sort('inactive state DESC', Person.inactive, Person.state.desc())
        p.add_sort('inactive state ASC', Person.inactive, Person.state)
        
        assert len(p._sortdd) == 6, len(p._sortdd)
    
    def test_reset_url(self):
        
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
            Person.lastname,
            sort='both'
        )
        p.add_tablecol(
            YesNo('Inactive'),
            Person.inactive,
            sort='drop-down'
        )
        p.add_col(
            'Sort Order',
            Person.sortorder,
        )
        
        p.add_sort('inactive state DESC', Person.inactive, Person.state.desc())
        p.add_sort('inactive state ASC', Person.inactive, Person.state)