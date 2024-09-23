from sqlalchemy import Column, Integer, String, TIMESTAMP
from db.connection import Base

# Class to build table for Vehicles
class Vehicle(Base):
    __tablename__ = 'vehicles'

    vehicle_id = Column(Integer, primary_key=True, index=True)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    registration_number = Column(String(50), nullable=False, unique=True)
    status = Column(String(20), nullable=False)
    mileage = Column(Integer, nullable=False)
    fuel_type = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)