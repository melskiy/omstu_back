from sqlalchemy import Column, Integer, Numeric, ForeignKey, Boolean, UniqueConstraint
from src.models.base import Base
from sqlalchemy.orm import relationship

from src.models.operation_type import OperationType


class Operation(Base):
    __tablename__ = 'operations'
    __table_args__ = (
        UniqueConstraint(
            'operation_type_id',
            'operation_result',
            'operation_amount',
            name='operations_unique'
        ),
    )
    operation_id = Column(Integer, primary_key=True)
    operation_type_id = Column(Integer, ForeignKey("operation_types.operation_type_id"))
    operation_result = Column(Boolean)
    operation_amount = Column(Numeric(15, 2))
    operation_type = relationship('OperationType')
