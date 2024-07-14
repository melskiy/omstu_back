from sqlalchemy import Column, Integer, SmallInteger, String, ForeignKey, UniqueConstraint
from src.models.base import Base
from sqlalchemy.orm import relationship

from src.models.terminal_type import TerminalType
from src.models.city import City


class Terminal(Base):
    __tablename__ = 'terminals'
    __table_args__ = (
        UniqueConstraint(
            'terminal_type_id',
            'city_id',
            'terminal_address',
            name='terminals_unique'
        ),
    )
    terminal_id = Column(Integer, primary_key=True)
    terminal_type_id = Column(SmallInteger, ForeignKey('terminal_types.terminal_type_id'))
    city_id = Column(Integer, ForeignKey('cities.city_id'))
    terminal_address = Column(String(250))
    terminal_type = relationship('TerminalType')
    city = relationship('City')
