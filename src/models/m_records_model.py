from sqlalchemy import Column, Integer, String, Date, DECIMAL, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from db.connection import Base

# Class to build table for Maintenance Records
class MaintenanceRecord(Base):
    __tablename__ = 'maintenance_records'

    maintenance_id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.driver_id'), nullable=False)
    maintenance_type = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    cost = Column(DECIMAL(10, 2), nullable=False)
    maintenance_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Method to convert SQL entry into a dictionary
    def to_dict(self):
        return {
            "maintenance_id": self.maintenance_id,
            "vehicle_id": self.vehicle_id,
            "driver_id": self.driver_id,
            "maintenance_type": self.maintenance_type,
            "description": self.description,
            "cost": self.cost,
            "maintenance_date": self.maintenance_date,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }