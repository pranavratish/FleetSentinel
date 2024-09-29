from sqlalchemy.orm import Session
from models.m_records_model import MaintenanceRecord
from models.vehicle_model import Vehicle
from models.driver_model import Driver

# Function to create a new maintenance record
def create_maintenance_record(db: Session, data: dict):
    # Validate vehicle and driver IDs
    vehicle_id = data.get('vehicle_id')
    driver_id = data.get('driver_id')

    # Ensure vehicle exists
    if vehicle_id:
        vehicle = db.query(Vehicle).filter_by(vehicle_id=vehicle_id).first()
        if not vehicle:
            raise ValueError('Assigned vehicle does not exist.')

    # Ensure driver exists
    if driver_id:
        driver = db.query(Driver).filter_by(driver_id=driver_id).first()
        if not driver:
            raise ValueError('Assigned driver does not exist.')

    # Create new maintenance record
    new_record = MaintenanceRecord(**data)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

# Function to retrieve a maintenance record by ID
def get_maintenance_record(db: Session, record_id: int):
    return db.query(MaintenanceRecord).filter(MaintenanceRecord.maintenance_id == record_id).first()

# Function to update a maintenance record
def update_maintenance_record(db: Session, record_id: int, data: dict):
    record = get_maintenance_record(db, record_id)
    if not record:
        return None

    # Update record attributes
    for key, value in data.items(): 
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record

# Function to delete a maintenance record
def delete_maintenance_record(db: Session, record_id: int):
    record = get_maintenance_record(db, record_id)
    if record:
        db.delete(record)
        db.commit()
    return record
