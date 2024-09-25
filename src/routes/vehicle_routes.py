import contextlib
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import String, or_
from sqlalchemy.orm import Session
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

# fetches the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# handles the "Vehicle not found" error
def handle_vehicle_not_found(vehicle):
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

# creates a new vehicle
@vehicle_bp.route('/vehicles', methods=['POST'])
def create_vehicle_endpoint():
    with contextlib.closing(next(get_db())) as db:
        data = request.get_json()
        new_vehicle = create_vehicle(db, data)
        return jsonify(new_vehicle.to_dict()), 201

# returns a vehicle by ID
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle_by_id_endpoint(vehicle_id):
    with contextlib.closing(next(get_db())) as db:
        vehicle = get_vehicle(db, vehicle_id=vehicle_id)
        not_found = handle_vehicle_not_found(vehicle)
        if not_found:
            return not_found
        return jsonify(vehicle.to_dict())

# more accessible search function and table display of rows with pagination
@vehicle_bp.route('/vehicles/search', methods=['GET'])
def search_vehicles():
    with contextlib.closing(next(get_db())) as db:
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
def update_vehicle_endpoint(vehicle_id):
    with contextlib.closing(next(get_db())) as db:
        # Get the data from the request (only the fields to be updated will be sent)
        data = request.get_json()
        
        # Retrieve the vehicle to be updated
        updated_vehicle = get_vehicle(db, vehicle_id=vehicle_id)
        
        # If the vehicle doesn't exist, handle the "not found" case
        not_found = handle_vehicle_not_found(updated_vehicle)
        if not_found:
            return not_found
        
        # Loop through the provided data and update only the fields that are present
        for key, value in data.items():
            if value:  # Only update the field if the new value is provided (non-null)
                setattr(updated_vehicle, key, value)
        
        # Commit the changes to the database
        db.commit()
        
        # Refresh the updated vehicle entry to reflect the changes
        db.refresh(updated_vehicle)
        
        # Return the updated vehicle as a JSON response
        return jsonify(updated_vehicle.to_dict())

# deletes a vehicle
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle_endpoint(vehicle_id):
    with contextlib.closing(next(get_db())) as db:
        deleted_vehicle = delete_vehicle(db, vehicle_id=vehicle_id)
        not_found = handle_vehicle_not_found(deleted_vehicle)
        if not_found:
            return not_found
        return jsonify({'message': 'Vehicle deleted successfully'})
