from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.orm import Session
from db.connection import SessionLocal
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
    db: Session = next(get_db())
    data = request.get_json()
    new_vehicle = create_vehicle(db, data)
    db.close()
    return jsonify(new_vehicle.to_dict()), 201

# returns a vehicle by ID
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle_by_id_endpoint(vehicle_id):
    db: Session = next(get_db())
    vehicle = get_vehicle(db, vehicle_id=vehicle_id)
    not_found = handle_vehicle_not_found(vehicle)
    if not_found:
        return not_found
    db.close()
    return jsonify(vehicle)

# updates a vehicles details
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle_endpoint(vehicle_id):
    db: Session = next(get_db())
    data = request.get_json()
    updated_vehicle = update_vehicle(db, vehicle_id=vehicle_id, data=data)
    not_found = handle_vehicle_not_found(updated_vehicle)
    if not_found:
        return not_found
    db.close
    return jsonify(updated_vehicle)

# deletes a vehicle
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle_endpoint(vehicle_id):
    db: Session = next(get_db())
    deleted_vehicle = delete_vehicle(db, vehicle_id=vehicle_id)
    not_found = handle_vehicle_not_found(deleted_vehicle)
    if not_found:
        return not_found
    db.close()
    return jsonify({'message': 'Vehicle deleted successfully'})
