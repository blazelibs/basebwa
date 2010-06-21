from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.sql as sasql
import savalidation as saval

class DeclarativeBase(saval.DeclarativeBase):
    
    id = sa.Column(sa.Integer, primary_key=True)
    createdts = sa.Column(sa.DateTime, nullable=False, server_default=sasql.text('CURRENT_TIMESTAMP'))
    updatedts = sa.Column(sa.DateTime, onupdate=datetime.now)

def declarative_base(*args, **kwargs):
    kwargs.setdefault('cls', DeclarativeBase)
    return saval.declarative_base(*args, **kwargs)

    