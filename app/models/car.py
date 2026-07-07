from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime
from app.database.database import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    mark = Column(String, nullable=True)
    model = Column(String, nullable=True)
    generation = Column(String, nullable=True)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    url = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    mileage = Column(Integer, nullable=True)
    specs = Column(String, nullable=True)
    parsed_at = Column(DateTime, default=datetime.utcnow)
