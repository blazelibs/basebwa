from werkzeug import Client, BaseResponse, create_environ
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, SmallInteger, DateTime, \
    UniqueConstraint, ForeignKey, String
from pysapptestapp.applications import make_wsgi
from pysmvt import db, getview
from pysmvt.utils import wrapinapp
from pysapp.modules.datagrid.utils import DataGrid
from pysmvt.htmltable import Col, YesNo
from _supporting import Person, Base, assertEqualSQL, dodiff

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



class TestFunctional(object):
    
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
    def test_html_table(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=firstname', 'http://localhost'))

        expect = """<table cellpadding="0" cellspacing="0" summary="">
    <thead>
        <tr>
            <th><a href="/foo?page=1&perpage=5&sort=-firstname" class="sort-desc">First Name</a></th>
            <th><a href="/foo?page=1&perpage=5&sort=lastname" class="sort-asc">Last Name</a></th>
            <th>Inactive</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>fn001</td>
            <td>ln001</td>
            <td>no</td>
        </tr>
        <tr>
            <td>fn002</td>
            <td>ln002</td>
            <td>no</td>
        </tr>
        <tr>
            <td>fn003</td>
            <td>ln003</td>
            <td>no</td>
        </tr>
        <tr>
            <td>fn004</td>
            <td>ln004</td>
            <td>no</td>
        </tr>
        <tr>
            <td>fn005</td>
            <td>ln005</td>
            <td>no</td>
        </tr>
    </tbody>
</table>"""

        assert p.html_table == expect

    @wrapinapp(app)
    def test_html_table_desc_sort(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=-firstname', 'http://localhost'))

        expect = """<tr>
            <th><a href="/foo?page=1&perpage=5&sort=firstname" class="sort-asc">First Name</a></th>
            <th><a href="/foo?page=1&perpage=5&sort=lastname" class="sort-asc">Last Name</a></th>
            <th>Inactive</th>
        </tr>"""
        assert expect in p.html_table

    @wrapinapp(app)
    def test_html_filter_controls(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=firstname&filteron=firstname&filteronop=eq&filterfor=test', 'http://localhost'))
        
        expected = """<div class="datagrid-filter-controls-wrapper">
    <select class="datagrid-filteron" name="filteron">
        <option value=""></option>
        <option value="firstname" selected="selected">First Name</option>
        <option value="lastname">Last Name</option>
        
    </select>
    <select class="datagrid-filteronop" name="filteronop">
        <option value=""></option>
        <option value="eq" selected="selected">=</option>
        <option value="ne">!=</option>
        <option value="lt">&lt;</option>
        <option value="lte">&lt;=</option>
        <option value="gt">&gt;</option>
        <option value="gte">&gt;=</option>
    </select>
    <input type="text" class="datagrid-filterfor" name="filterfor" value="test"/>
</div>"""
        assertEqualSQL(p.html_filter_controls, expected)

    @wrapinapp(app)
    def test_html_filter_controls(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=firstname&filteron=firstname&filteronop=eq&filterfor=test', 'http://localhost'))
        
        html = p.html_filter_controls
        assert """<select class="datagrid-filteron" name="filteron">
            <option value="">&nbsp;</option>
            <option value="firstname" selected="selected">First Name</option>
            <option value="lastname">Last Name</option>
            
        </select>""" in html, html
        
        expected = """<select class="datagrid-filteronop" name="filteronop">
        <option value="">&nbsp;</option>
        <option value="eq" selected="selected">=</option>
        <option value="ne">!=</option>
        <option value="lt">&lt;</option>
        <option value="lte">&lt;=</option>
        <option value="gt">&gt;</option>
        <option value="gte">&gt;=</option>
    </select>"""
        assert expected in html, dodiff(html, expected)
    
        assert '<input type="text" class="datagrid-filterfor" name="filterfor" value="test"/>' in html
        
    @wrapinapp(app)
    def test_html_sort_controls(self):
        p = self.get_dg()
        p.add_sort('inactive state DESC', Person.inactive, Person.state.desc())
        p.add_sort('inactive state ASC', Person.inactive, Person.state)
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=firstname&filteron=firstname&filteronop=eq&filterfor=test', 'http://localhost'))
        
        expected = """<div class="datagrid-sort-controls-wrapper expand-around-floats">
    <div class="sortdd-wrapper">
        <select class="datagrid-sort" name="sortdd">
            <option value="">&nbsp;</option>
            <option value="inactiveasc">Inactive ASC</option>
            <option value="inactivedesc">Inactive DESC</option>
            <option value="inactivestatedesc">inactive state DESC</option>
            <option value="inactivestateasc">inactive state ASC</option>
            
        </select><br />
        <label>Sort:</label>
    </div>
</div>"""
        assertEqualSQL(p.html_sort_controls, expected)
    
    @wrapinapp(app)
    def test_no_sort_controls(self):
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
        )
        p.add_col(
            'Sort Order',
            tbl.c.sortorder,
        )
        assert not p.html_sort_controls
    
    @wrapinapp(app)
    def test_no_filter_controls(self):
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
            tbl.c.firstname
            )
        p.add_tablecol(
            Col('Last Name'),
            Person.lastname
        )
        p.add_tablecol(
            YesNo('Inactive'),
            Person.inactive,
        )
        p.add_col(
            'Sort Order',
            tbl.c.sortorder,
        )
        assert not p.html_filter_controls
        
    @wrapinapp(app)
    def test_html_pager_controls_upper(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=20&page=3', 'http://localhost'))
        
        html = p.html_pager_controls_upper
        assert """<select class="datagrid-pager-upper" name="page">
            <option value="1">1 of 5</option>
            <option value="2">2 of 5</option>
            <option value="3" selected="selected">3 of 5</option>
            <option value="4">4 of 5</option>
            <option value="5">5 of 5</option>
            
        </select>""" in html 
        
        assert '<input type="text" class="datagrid-perpage" name="perpage" value="20"/>' in html

    @wrapinapp(app)
    def test_html_pager_controls_lower(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=20&page=3', 'http://localhost'))

        html = p.html_pager_controls_lower
        assert '<a class="pager-link-first" href="/foo?page=1&perpage=20">&lt;&lt; first</a>' \
            in html
        assert '<a class="pager-link-previous" href="/foo?page=2&perpage=20">&lt; previous</a>' \
            in html
        assert '<a class="pager-link-next" href="/foo?page=4&perpage=20">next &gt;</a>' \
            in html
        assert '<a class="pager-link-last" href="/foo?page=5&perpage=20">last &gt;&gt;</a>' \
            in html
        
        p._replace_environ(create_environ('/foo?perpage=20&page=1', 'http://localhost'))
        expected = """<ul class="datagrid-pager-controls-lower-wrapper">
        <li class="dead">&lt;&lt; first</li>
        <li class="dead">&lt; previous</li>
        <li><a class="pager-link-next" href="/foo?page=2&perpage=20">next &gt;</a></li>
        <li><a class="pager-link-last" href="/foo?page=5&perpage=20">last &gt;&gt;</a></li>
</ul>"""
        assertEqualSQL(p.html_pager_controls_lower, expected)
        
        p._replace_environ(create_environ('/foo?perpage=20&page=5', 'http://localhost'))
        
        html = p.html_pager_controls_lower
        assert '<a class="pager-link-first" href="/foo?page=1&perpage=20">&lt;&lt; first</a>' \
            in html
        assert '<a class="pager-link-previous" href="/foo?page=4&perpage=20">&lt; previous</a>' \
            in html
        assert '<li class="dead">next &gt;</li>' \
            in html
        assert '<li class="dead">last &gt;&gt;</li>' \
            in html
    
    @wrapinapp(app)
    def test_blank_sortdd(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?sortdd=&page=1&perpage=10', 'http://localhost'))
        
        recstr = ''.join([str(r) for r in p.records])
        assert 'fn001' in recstr
        assert 'fn010' in recstr
        assert 'fn011' not in recstr
    
    @wrapinapp(app)
    def test_blank_sortdd_header_sort(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?sortdd=&page=1&perpage=10&sort=-firstname', 'http://localhost'))
        
        recstr = ''.join([str(r) for r in p.records])
        assert 'fn100' in recstr
        assert 'fn091' in recstr
        assert 'fn090' not in recstr