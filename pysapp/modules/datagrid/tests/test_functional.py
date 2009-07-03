from werkzeug import Client, BaseResponse, create_environ
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, SmallInteger, DateTime, \
    UniqueConstraint, ForeignKey, String
from pysapptestapp.applications import make_wsgi
from pysmvt import db, getview
from pysmvt.utils import wrapinapp
from pysapp.modules.datagrid.utils import DataGrid
from pysmvt.htmltable import Col, YesNo
from _supporting import Person, Base

app = make_wsgi('Test')
c = Client(app, BaseResponse)
    
@wrapinapp(app)
def setup_module():
    Base.metadata.create_all(db.engine)
    for x in range(1, 101):
        p = Person()
        p.firstname = 'fn%03d' % x
        p.lastname = 'ln%03d' % x
        db.sess.add(p)
    db.sess.commit()



class TestDb(object):
    
    def get_dg(self):
        tbl = Person.__table__
        p = DataGrid(
            db.sess.execute,
            )
        p.add_col(
            'Id',
            tbl.c.id,
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
        p.add_tablecol(
            YesNo('Inactive'),
            Person.inactive,
            sort='drop-down'
        )
        p.add_col(
            'Sort Order',
            tbl.c.sortorder,
        )
        return p
    
    @wrapinapp(app)
    def test_records(self):
        tbl = Person.__table__
        qobj = db.sess.query(tbl)
        count = qobj.count()
        assert count == 100, count
        
        qobj = db.sess.query(Person.id, Person.firstname)
        count = qobj.count()
        assert count == 100, count

        p = self.get_dg()
        
        assert p.count == 100
        records = p.records
        assert len(records) == p.count

    @wrapinapp(app)
    def test_html(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=firstname', 'http://localhost'))
        r = p.records

        print p.html_table