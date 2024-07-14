from sqlalchemy import Column, Integer, String, DateTime, Date, SmallInteger, Boolean, Numeric
from src.models.base import Base


class PredictView(Base):
    __tablename__ = 'predict_view'
    id_transaction = Column(Integer, primary_key=True)
    date = Column(DateTime)
    city = Column(Integer)
    card = Column(String(8))
    client = Column(String(7))
    date_of_birth = Column(Date)
    operation_type = Column(SmallInteger)
    terminal_type = Column(Integer)
    operation_result = Column(Boolean)
    amount = Column(Numeric(15, 2))
    fraud_probability = Column(Numeric(3, 2))
