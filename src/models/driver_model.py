from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from db.connection import Base

# Class to build table for Drivers
class Driver(Base):
    __tablename__ = 'drivers'

    driver_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    license_number = Column(String(50), nullable=False, unique=True)
    license_expiry_date = Column(Date, nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    assigned_vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'), nullable=True)  # References vehicles table (foreign key)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Method to convert SQL entry into a dictionary
    def to_dict(self):
        return {
            "driver_id": self.driver_id,
            "name": self.name,
            "license_number": self.license_number,
            "license_expiry_date": self.license_expiry_date,
            "phone_number": self.phone_number,
            "email": self.email,
            "assigned_vehicle_id": self.assigned_vehicle_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }