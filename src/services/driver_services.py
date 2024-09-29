from sqlalchemy.orm import Session
from models.driver_model import Driver
from models.vehicle_model import Vehicle

# Function to create a new driver
def create_driver(db: Session, data: dict):
    # Validate the assigned vehicle ID if provided
    assigned_vehicle_id = data.get('assigned_vehicle_id')

    if assigned_vehicle_id:
        assigned_vehicle = db.query(Vehicle).filter_by(vehicle_id=assigned_vehicle_id).first()
        if not assigned_vehicle:
            raise ValueError('Assigned vehicle does not exist.')

    new_driver = Driver(**data)
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver
 
# Function to retrieve a driver by ID
def get_driver(db: Session, driver_id: int):
    return db.query(Driver).filter(Driver.driver_id == driver_id).first()

# Function to update a driver's details
def update_driver(db: Session, driver_id: int, data: dict):
    driver = get_driver(db, driver_id)
    if not driver:
        return None  # Return None if driver is not found
    for key, value in data.items():
        setattr(driver, key, value)
    db.commit()
    db.refresh(driver)
    return driver

# Function to delete a driver
def delete_driver(db: Session, driver_id: int):
    driver = get_driver(db, driver_id)
    if driver:
        db.delete(driver)
        db.commit()
    return driver
