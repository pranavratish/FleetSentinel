import contextlib
from functools import wraps
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import or_, String
from db.connection import SessionLocal
from models.m_records_model import MaintenanceRecord
from services.m_records_services import (
    create_maintenance_record,
    get_maintenance_record,
    update_maintenance_record,
    delete_maintenance_record
)

# declares Blueprint for maintenance record routes
maintenance_bp = Blueprint('maintenance', __name__)

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

# General helper function to handle "Not found" cases
def not_found(entity, entity_name="Entity"):
    if not entity:
        return jsonify({'error': f'{entity_name} not found'}), 404

# serves the HTML form for creating a new maintenance record
@maintenance_bp.route('/maintenance/new', methods=['GET'])
def new_maintenance_record_form():
    return render_template('maintenance_record_create_form.html')

# creates a new maintenance record
@maintenance_bp.route('/maintenance', methods=['POST'])
@with_db
def create_maintenance_record_endpoint(db):
    data = request.get_json()
    try:
        new_record = create_maintenance_record(db, data)
        return jsonify(new_record.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

# returns a maintenance record by ID
@maintenance_bp.route('/maintenance/<int:record_id>', methods=['GET'])
@with_db
def get_maintenance_record_by_id_endpoint(db, record_id):
    record = get_maintenance_record(db, record_id=record_id)
    return not_found(record, "Maintenance Record") or jsonify(record.to_dict())

# updates a maintenance record's details (supports partial updates)
@maintenance_bp.route('/maintenance/<int:record_id>', methods=['PUT'])
@with_db
def update_maintenance_record_endpoint(db, record_id):
    data = request.get_json()
    updated_record = update_maintenance_record(db, record_id=record_id, data=data)
    return not_found(updated_record, "Maintenance Record") or jsonify(updated_record.to_dict())

# deletes a maintenance record
@maintenance_bp.route('/maintenance/<int:record_id>', methods=['DELETE'])
@with_db
def delete_maintenance_record_endpoint(db, record_id):
    deleted_record = delete_maintenance_record(db, record_id=record_id)
    return not_found(deleted_record, "Maintenance Record") or jsonify({'message': 'Maintenance record deleted successfully'})

# more accessible search function and table display of rows with pagination
@maintenance_bp.route('/maintenance/search', methods=['GET'])
@with_db
def search_maintenance_records(db):
    search_term = request.args.get('query', '')

    # List of attributes to search
    search_fields = [MaintenanceRecord.maintenance_type, MaintenanceRecord.description, MaintenanceRecord.notes]

    query = db.query(MaintenanceRecord)

    # Search for the term in all specified fields
    if search_term:
        search_filters = []
        for field in search_fields:
            if isinstance(field.type, String):
                search_filters.append(field.ilike(f"%{search_term}%"))

        # Apply all search filters with OR logic
        query = query.filter(or_(*search_filters))

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    skip = (page - 1) * per_page

    records = query.offset(skip).limit(per_page).all()
    total_records = query.count()

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total_records': total_records,
        'records': [record.to_dict() for record in records]
    })
