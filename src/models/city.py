from sqlalchemy import Column, Integer, String, UniqueConstraint
from src.models.base import Base

from sqlalchemy.orm import relationship


class City(Base):
    __tablename__ = 'cities'
    __table_args__ = (
        UniqueConstraint(
            'city_name',
            name='cities_unique'
        ),
    )
    city_id = Column(Integer, primary_key=True)
    city_name = Column(String)
