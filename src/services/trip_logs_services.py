from sqlalchemy.orm import Session
from models.trip_logs_model import TripLog
from models.vehicle_model import Vehicle
from models.driver_model import Driver

# Function to create a new trip log
def create_trip_log(db: Session, data: dict):
    # Validate the vehicle and driver IDs if provided
    assigned_vehicle_id = data.get('vehicle_id')
    assigned_driver_id = data.get('driver_id')

    if assigned_vehicle_id:
        assigned_vehicle = db.query(Vehicle).filter_by(vehicle_id=assigned_vehicle_id).first()
        if not assigned_vehicle:
            raise ValueError('Assigned vehicle does not exist.')

    if assigned_driver_id:
        assigned_driver = db.query(Driver).filter_by(driver_id=assigned_driver_id).first()
        if not assigned_driver:
            raise ValueError('Assigned driver does not exist.')

    new_trip_log = TripLog(**data)
    db.add(new_trip_log)
    db.commit()
    db.refresh(new_trip_log)
    return new_trip_log

# Function to retrieve a trip log by ID
def get_trip_log(db: Session, trip_id: int):
    return db.query(TripLog).filter(TripLog.trip_id == trip_id).first()

# Function to update a trip log's details
def update_trip_log(db: Session, trip_id: int, data: dict):
    trip_log = get_trip_log(db, trip_id)
    if not trip_log:
        return None  # Return None if trip log is not found
    for key, value in data.items():
        setattr(trip_log, key, value)
    db.commit()
    db.refresh(trip_log)
    return trip_log

# Function to delete a trip log
def delete_trip_log(db: Session, trip_id: int):
    trip_log = get_trip_log(db, trip_id)
    if trip_log:
        db.delete(trip_log)
        db.commit()
    return trip_log