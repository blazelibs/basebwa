from datetime import datetime
from sqlalchemy import Column, Integer, Unicode, SmallInteger, DateTime, \
    UniqueConstraint, ForeignKey, String, Float, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from pysmvt import db
import difflib

Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column('last_name', String(50))
    inactive = Column(SmallInteger)
    state = Column(String(50))
    status = Column(Integer)
    address = Column(Integer)
    createdts = Column(DateTime)
    sortorder = Column(Integer)
    floatcol = Column(Float)
    numericcol = Column(Numeric)
    boolcol = Column(Boolean)
    
    def __repr__(self):
        return '<Person: "%s, created: %s">' % (self.id, self.createdts)


class Email(Base):
    __tablename__ = 'emails'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, nullable=False)
    email = Column(String(50), nullable=False)

class Status(Base):
    __tablename__ = 'statuses'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, nullable=False)
    email = Column(String(50), nullable=False)    

def prettifySQL(sql):
    """Returns a prettified version of the SQL as a list of lines to help
    in creating a useful diff between two SQL statements."""
    pretty = []
    for line in sql.split('\n'):
        pretty.extend([ "%s,\n" % x for x in line.split(',')])
    return pretty

def assertEqualSQL(sql, correct_sql):
    sql_split = prettifySQL(sql)
    correct_sql_split = prettifySQL(correct_sql)
    sql_diff = ''.join(list(
        difflib.unified_diff(correct_sql_split, sql_split)
    ))
    failure_message = "%r != %r\n" % (sql, correct_sql) + sql_diff
    assert sql == correct_sql, failure_message

def dodiff(actual, expected):
    return '\n'.join(list(
        difflib.unified_diff(actual.split('\n'), expected.split('\n'))
    ))