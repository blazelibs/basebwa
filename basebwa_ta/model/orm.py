import sqlalchemy as sa

import savalidation.validators as val
from sqlalchemybwp import db
from sqlalchemybwp.lib.declarative import declarative_base, DefaultMixin
from sqlalchemybwp.lib.decorators import ignore_unique, transaction

Base = declarative_base()

class Widget(Base, DefaultMixin):
    __tablename__ = 'basebwa_ta_widgets'

    widget_type = sa.Column(sa.Unicode(255), nullable=False)
    color = sa.Column(sa.Unicode(255), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)

    val.validates_constraints()