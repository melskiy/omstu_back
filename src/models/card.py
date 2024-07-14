from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

from src.models.client import Client


class Card(Base):
    __tablename__ = 'cards'
    card_number = Column(String(8), primary_key=True)
    client_id = Column(String(7), ForeignKey('clients.client_id'))
    phone_hashed = Column(String(8))
    client = relationship('Client')
