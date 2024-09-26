import contextlib
from functools import wraps
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import String, or_
from db.connection import SessionLocal
from models.driver_model import Driver
from services.driver_services import (
    create_driver,
    get_driver,
    update_driver,
    delete_driver,
)

# declares Blueprint for driver routes
driver_bp = Blueprint('driver', __name__)

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

# Helper function to handle "Driver not found" case
def not_found(driver):
    if not driver:
        return jsonify({'error': 'Driver not found'}), 404

# serves the HTML form for creating a new driver
@driver_bp.route('/drivers/new', methods=['GET'])
def new_driver_form():
    return render_template('driver_create_form.html')

# renders the table display and search form HTML file
@driver_bp.route('/drivers/search/form', methods=['GET'])
def drivers_table_form():
    return render_template('driver_search_form.html')

# renders the update driver HTML form
@driver_bp.route('/drivers/<int:driver_id>/update', methods=['GET'])
def update_driver_form(driver_id):
    return render_template('driver_update_form.html')

# creates a new driver
@driver_bp.route('/drivers', methods=['POST'])
@with_db
def create_driver_endpoint(db):
    data = request.get_json()
    new_driver = create_driver(db, data)
    return jsonify(new_driver.to_dict()), 201

# returns a driver by ID
@driver_bp.route('/drivers/<int:driver_id>', methods=['GET'])
@with_db
def get_driver_by_id_endpoint(db, driver_id):
    driver = get_driver(db, driver_id=driver_id)
    if not_found(driver):
        return not_found(driver)
    return jsonify(driver.to_dict())

# more accessible search function and table display of rows with pagination
@driver_bp.route('/drivers/search', methods=['GET'])
@with_db
def search_drivers(db):
    search_term = request.args.get('query', '')

    # List of attributes to search
    search_fields = [Driver.first_name, Driver.last_name, Driver.license_number]

    query = db.query(Driver)

    # Search for the term in all specified fields
    if search_term:
        search_filters = []
        for field in search_fields:
            search_filters.append(field.ilike(f"%{search_term}%"))
        query = query.filter(or_(*search_filters))

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    skip = (page - 1) * per_page

    drivers = query.offset(skip).limit(per_page).all()
    total_drivers = query.count()

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total_drivers': total_drivers,
        'drivers': [driver.to_dict() for driver in drivers]
    })

# updates a driver's details (supports partial updates)
@driver_bp.route('/drivers/<int:driver_id>', methods=['PUT'])
@with_db
def update_driver_endpoint(db, driver_id):
    data = request.get_json()
    updated_driver = update_driver(db, driver_id=driver_id, data=data)
    if not_found(updated_driver):
        return not_found(updated_driver)
    return jsonify(updated_driver.to_dict())

# deletes a driver
@driver_bp.route('/drivers/<int:driver_id>', methods=['DELETE'])
@with_db
def delete_driver_endpoint(db, driver_id):
    deleted_driver = delete_driver(db, driver_id=driver_id)
    if not_found(deleted_driver):
        return not_found(deleted_driver)
    return jsonify({'message': 'Driver deleted successfully'})