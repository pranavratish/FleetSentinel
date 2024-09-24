from sqlalchemy.orm import Session
from models.vehicle_model import Vehicle

# Function to create new vehicle
def create_vehicle(db: Session, data: dict):
    new_vehicle = Vehicle(**data)
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle

# Function to return vehicle by vehicle ID
def get_vehicle(db: Session, vehicle_id: int):
    return db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()

# not functional as the query logic is implemented in the search function in the routes file
# # Retrieve all vehicles in DB with pages
# def get_all_vehicles(db: Session, skip: int = 0, limit: int = 10):
#     return db.query(Vehicle).offset(skip).limit(limit).all()

# Function for updating vehicle entry
def update_vehicle(db: Session, vehicle_id: int, data: dict):
    vehicle = get_vehicle(db, vehicle_id)
    if vehicle:
        for key, value in data.items():
            setattr(vehicle, key, value)
        db.commit()
        db.refresh(vehicle)
    return vehicle

# Function for deletion of entry
def delete_vehicle(db: Session, vehicle_id = int):
    vehicle = get_vehicle(db, vehicle_id)
    if vehicle:
        db.delete(vehicle)
        db.commit()
    return vehicle