from sqlalchemy import Column, Integer, ForeignKey, Table
from .base import Base

event_member = Table(
    'event_members', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)
