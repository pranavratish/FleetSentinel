from sqlalchemy.orm import Session
from models.driver_model import Driver

# Function to create a new driver
def create_driver(db: Session, data: dict):
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
    if driver:
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
