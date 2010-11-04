import sqlalchemy as sa

import savalidation.validators as val
from sqlalchemybwc import db
from sqlalchemybwc.lib.declarative import declarative_base, DefaultMixin
from sqlalchemybwc.lib.decorators import ignore_unique, transaction

Base = declarative_base()

class Widget(Base, DefaultMixin):
    __tablename__ = 'basebwa_ta_widgets'

    widget_type = sa.Column(sa.Unicode(255), nullable=False)
    color = sa.Column(sa.Unicode(255), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)

    val.validates_constraints()
