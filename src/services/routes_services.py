from sqlalchemy.orm import Session
from models.routes_model import Route

# Function to create a new route
def create_route(db: Session, data: dict):
    new_route = Route(**data)
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    return new_route

# Function to retrieve a route by ID
def get_route(db: Session, route_id: int):
    return db.query(Route).filter(Route.route_id == route_id).first()

# Function to update a route's details
def update_route(db: Session, route_id: int, data: dict):
    route = get_route(db, route_id)
    if not route:
        return None  # Return None if route is not found
    for key, value in data.items():
        setattr(route, key, value)
    db.commit()
    db.refresh(route)
    return route

# Function to delete a route
def delete_route(db: Session, route_id: int):
    route = get_route(db, route_id)
    if route:
        db.delete(route)
        db.commit()
    return route
