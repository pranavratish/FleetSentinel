from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Text, Float
from sqlalchemy.sql import func
from db.connection import Base

class TripLog(Base):
    __tablename__ = 'trip_logs'

    trip_id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.driver_id'), nullable=False)
    route_id = Column(Integer, ForeignKey('routes.route_id'), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    mileage_start = Column(Integer, nullable=False)
    mileage_end = Column(Integer)
    status = Column(String(20), nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'trip_id': self.trip_id,
            'vehicle_id': self.vehicle_id,
            'driver_id': self.driver_id,
            'route_id': self.route_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'mileage_start': self.mileage_start,
            'mileage_end': self.mileage_end,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }