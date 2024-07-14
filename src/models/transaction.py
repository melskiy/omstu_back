from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from src.models.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from src.models.card import Card
from src.models.terminal import Terminal
from src.models.operation import Operation


class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer, primary_key=True)
    terminal_id = Column(Integer, ForeignKey('terminals.terminal_id'))
    transaction_date = Column(TIMESTAMP)
    card_number = Column(String(8), ForeignKey('cards.card_number'))
    operation_id = Column(Integer, ForeignKey('operations.operation_id'))
    transaction_fraud_probability = Column(Numeric(3, 2))
    operation = relationship('Operation')
    terminal = relationship('Terminal')
    card = relationship('Card')
