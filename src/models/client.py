from sqlalchemy import Column, String, Date
from src.models.base import Base


class Client(Base):
    __tablename__ = 'clients'
    client_id = Column(String(7), primary_key=True)
    passport_hashed = Column(String(8))
    passport_valid_to = Column(Date)
    date_of_birth = Column(Date)
