import contextlib
from functools import wraps
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import String, or_, asc, desc
from db.connection import SessionLocal
from models.vehicle_model import Vehicle
from services.vehicle_services import (
    create_vehicle,
    get_vehicle,
    update_vehicle,
    delete_vehicle
)

# declares Blueprint for vehicle routes
vehicle_bp = Blueprint('vehicle', __name__)

# Helper function to fetch the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# fetches the DB session with a decorator
def with_db(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with contextlib.closing(next(get_db())) as db:
            return f(db, *args, **kwargs)
    return decorated_function

# Helper function to handle "Vehicle not found" case
def vehicle_not_found_response(vehicle):
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

# serves the HTML form for creating a new vehicle
@vehicle_bp.route('/vehicles/new', methods=['GET'])
def new_vehicle_form():
    return render_template('vehicle_create_form.html')

# renders the table display and search form HTML file
@vehicle_bp.route('/vehicles/search/form', methods=['GET'])
def vehicles_table_form():
    return render_template('vehicle_search_form.html')

# renders the update vehicle HTML form and passes the vehicle data
@vehicle_bp.route('/vehicles/<int:vehicle_id>/update', methods=['GET'])
@with_db
@jwt_required()
def update_vehicle_form(db, vehicle_id):
    vehicle = get_vehicle(db, vehicle_id=vehicle_id)
    if vehicle_not_found_response(vehicle):
        return vehicle_not_found_response(vehicle)  # Return a 404 if the vehicle isn't found
    return render_template('vehicle_update_form.html', vehicle=vehicle)  # Pass the vehicle data to the template

# creates a new vehicle
@vehicle_bp.route('/vehicles', methods=['POST'])
@with_db
@jwt_required()
def create_vehicle_endpoint(db):
    data = request.get_json()
    new_vehicle = create_vehicle(db, data)
    return jsonify(new_vehicle.to_dict()), 201

# returns a vehicle by ID
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@with_db
@jwt_required()
def get_vehicle_by_id_endpoint(db, vehicle_id):
    vehicle = get_vehicle(db, vehicle_id=vehicle_id)
    return vehicle_not_found_response(vehicle) or jsonify(vehicle.to_dict())

# more accessible search, filtering, sorting, and table display of rows with pagination
@vehicle_bp.route('/vehicles/search', methods=['GET'])
@with_db
def search_vehicles(db):
    search_term = request.args.get('query', '')
    sort_by = request.args.get('sortBy', 'make')  # Default sort by vehicle make
    sort_order = request.args.get('sortOrder', 'asc')  # Default sort order ascending

    # List of attributes to search
    search_fields = [Vehicle.make, Vehicle.model, Vehicle.registration_number, Vehicle.status, Vehicle.fuel_type]

    query = db.query(Vehicle)

    # Search for the term in all specified fields
    if search_term:
        search_filters = []
        
        # Check if search_term is numeric to filter by vehicle_id or year
        if search_term.isdigit():
            search_filters.append(Vehicle.vehicle_id == int(search_term))
            search_filters.append(Vehicle.year == int(search_term))

        # Apply ILIKE to string fields
        for field in search_fields:
            search_filters.append(field.ilike(f"%{search_term}%"))
        
        query = query.filter(or_(*search_filters))

    # Apply sorting
    if sort_order == 'asc':
        query = query.order_by(asc(getattr(Vehicle, sort_by)))
    else:
        query = query.order_by(desc(getattr(Vehicle, sort_by)))

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    skip = (page - 1) * per_page

    vehicles = query.offset(skip).limit(per_page).all()
    total_vehicles = query.count()

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total_vehicles': total_vehicles,
        'vehicles': [vehicle.to_dict() for vehicle in vehicles]
    })

# Endpoint to get the mileage of a vehicle by ID
@vehicle_bp.route('/vehicles/<int:vehicle_id>/mileage', methods=['GET'])
@jwt_required()
def get_vehicle_mileage(vehicle_id):
    db = next(get_db())
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()

    if vehicle:
        return jsonify({'mileage': vehicle.mileage})
    return jsonify({'error': 'Vehicle not found'}), 404

# updates a vehicle's details (supports partial updates)
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@with_db
@jwt_required()
def update_vehicle_endpoint(db, vehicle_id):
    data = request.get_json()
    updated_vehicle = update_vehicle(db, vehicle_id=vehicle_id, data=data)
    return vehicle_not_found_response(updated_vehicle) or jsonify(updated_vehicle.to_dict())

# deletes a vehicle
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
@with_db
@jwt_required()
def delete_vehicle_endpoint(db, vehicle_id):
    deleted_vehicle = delete_vehicle(db, vehicle_id=vehicle_id)
    return vehicle_not_found_response(deleted_vehicle) or jsonify({'message': 'Vehicle deleted successfully'})