from sqlalchemy import Column, Integer, String, UniqueConstraint
from src.models.base import Base


class OperationType(Base):
    __tablename__ = 'operation_types'
    __table_args__ = (
        UniqueConstraint(
            'operation_type_name',
            name='operation_types_unique'
        ),
    )
    operation_type_id = Column(Integer, primary_key=True)
    operation_type_name = Column(String(15))
