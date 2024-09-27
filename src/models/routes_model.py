from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.sql import func
from db.connection import Base

# Class to build table for Routes
class Route(Base):
    __tablename__ = 'routes'

    route_id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    distance = Column(Float, nullable=False)
    estimated_duration = Column(Integer, nullable=False)  # Assuming it's in minutes
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Method to convert SQL entry into a dictionary
    def to_dict(self):
        return {
            "route_id": self.route_id,
            "origin": self.origin,
            "destination": self.destination,
            "distance": self.distance,
            "estimated_duration": self.estimated_duration,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }