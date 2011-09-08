from datetime import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime, \
    ForeignKey, UnicodeText
from sqlalchemy.sql import text
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base

from compstack.auth.model.orm import User
from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.declarative import declarative_base

Base = declarative_base()

class AuditRecord(Base):
    __tablename__ = 'audit_records'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('auth_users.id', name='fk_audit_records_to_user_id'), nullable=True)
    identifier = Column(Unicode(50), nullable=False)
    audit_text = Column(UnicodeText, nullable=False)
    comments = Column(Unicode(256))

    createdts = Column(DateTime, nullable=False, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    lastupdatets = Column(DateTime, onupdate=datetime.now)

    user = relation(User, lazy=False)
