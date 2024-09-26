import contextlib
from functools import wraps
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import String, or_
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

# helper function to handle "Vehicle not found" case
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

# renders the update vehicle HTML form
@vehicle_bp.route('/vehicles/<int:vehicle_id>/update', methods=['GET'])
def update_vehicle_form(vehicle_id):
    return render_template('vehicle_update_form.html')

# creates a new vehicle
@vehicle_bp.route('/vehicles', methods=['POST'])
@with_db
def create_vehicle_endpoint(db):
    data = request.get_json()
    new_vehicle = create_vehicle(db, data)
    return jsonify(new_vehicle.to_dict()), 201

# returns a vehicle by ID
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@with_db
def get_vehicle_by_id_endpoint(db, vehicle_id):
    vehicle = get_vehicle(db, vehicle_id=vehicle_id)
    not_found = vehicle_not_found_response(vehicle)
    if not_found:
        return not_found
    return jsonify(vehicle.to_dict())

# more accessible search function and table display of rows with pagination
@vehicle_bp.route('/vehicles/search', methods=['GET'])
@with_db
def search_vehicles(db):
    search_term = request.args.get('query', '')

    # List of attributes to search
    search_fields = [Vehicle.make, Vehicle.model, Vehicle.year, Vehicle.registration_number, Vehicle.status, Vehicle.fuel_type]

    query = db.query(Vehicle)

    # Search for the term in all specified fields
    if search_term:
        search_filters = []
        for field in search_fields:
            if isinstance(field.type, String):
                search_filters.append(field.ilike(f"%{search_term}%"))
            else:
                try:
                    # If the search term can be cast to a number, allow searching non-string fields
                    search_value = int(search_term)
                    search_filters.append(field == search_value)
                except ValueError:
                    continue

        # Apply all search filters with OR logic
        query = query.filter(or_(*search_filters))

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

# updates a vehicle's details (supports partial updates)
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@with_db
def update_vehicle_endpoint(db, vehicle_id):
    # Get the data from the request
    data = request.get_json()

    # Call the update_vehicle function from the service
    updated_vehicle = update_vehicle(db, vehicle_id=vehicle_id, data=data)

    # If the vehicle doesn't exist, handle the "not found" case
    not_found = vehicle_not_found_response(updated_vehicle)
    if not_found:
        return not_found

    # Return the updated vehicle as a JSON response
    return jsonify(updated_vehicle.to_dict())


# deletes a vehicle
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
@with_db
def delete_vehicle_endpoint(db, vehicle_id):
    deleted_vehicle = delete_vehicle(db, vehicle_id=vehicle_id)
    not_found = vehicle_not_found_response(deleted_vehicle)
    if not_found:
        return not_found
    return jsonify({'message': 'Vehicle deleted successfully'})