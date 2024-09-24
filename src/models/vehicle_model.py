from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
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
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False) # sets time automatically
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False) # updates time automatically

    # method to convert sql entry into python dict
    def to_dict(self):
        return {
            "vehicle_id": self.vehicle_id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "registration_number": self.registration_number,
            "status": self.status,
            "mileage": self.mileage,
            "fuel_type": self.fuel_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }