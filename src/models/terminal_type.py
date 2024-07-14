from sqlalchemy import Column, SmallInteger, String, UniqueConstraint
from src.models.base import Base


class TerminalType(Base):
    __tablename__ = 'terminal_types'
    __table_args__ = (
        UniqueConstraint(
            'terminal_type_name',
            name='terminal_types_unique'
        ),
    )
    terminal_type_id = Column(SmallInteger, primary_key=True)
    terminal_type_name = Column(String(3))
