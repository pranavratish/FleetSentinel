import contextlib
from functools import wraps
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, String, asc, desc
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
    return render_template('m_record_create_form.html')

@maintenance_bp.route('/maintenance/search/form', methods=['GET'])
def search_maintenance_form():
    return render_template('m_record_search_form.html')

# renders the update maintenance record HTML form
@maintenance_bp.route('/maintenance/<int:record_id>/update', methods=['GET'])
@with_db
@jwt_required()
def update_maintenance_record_form(db, record_id):
    maintenance_record = get_maintenance_record(db, record_id=record_id)
    if not maintenance_record:
        return not_found(maintenance_record, "Maintenance Record")
    return render_template('m_record_update_form.html', maintenance_record=maintenance_record)

# creates a new maintenance record
@maintenance_bp.route('/maintenance', methods=['POST'])
@with_db
@jwt_required()
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
@jwt_required()
def get_maintenance_record_by_id_endpoint(db, record_id):
    record = get_maintenance_record(db, record_id=record_id)
    return not_found(record, "Maintenance Record") or jsonify(record.to_dict())

# updates a maintenance record's details (supports partial updates)
@maintenance_bp.route('/maintenance/<int:record_id>', methods=['PUT'])
@with_db
@jwt_required()
def update_maintenance_record_endpoint(db, record_id):
    data = request.get_json()
    updated_record = update_maintenance_record(db, record_id=record_id, data=data)
    return not_found(updated_record, "Maintenance Record") or jsonify(updated_record.to_dict())

# deletes a maintenance record
@maintenance_bp.route('/maintenance/<int:record_id>', methods=['DELETE'])
@with_db
@jwt_required()
def delete_maintenance_record_endpoint(db, record_id):
    deleted_record = delete_maintenance_record(db, record_id=record_id)
    return not_found(deleted_record, "Maintenance Record") or jsonify({'message': 'Maintenance record deleted successfully'})

# more accessible search, filtering, sorting, and table display of rows with pagination
@maintenance_bp.route('/maintenance/search', methods=['GET'])
@with_db
def search_maintenance_records(db):
    search_term = request.args.get('query', '')
    sort_by = request.args.get('sortBy', 'maintenance_type')  # Default sort by maintenance_type
    sort_order = request.args.get('sortOrder', 'asc')  # Default order ascending

    # List of attributes to search for string fields
    search_fields = [MaintenanceRecord.maintenance_type, MaintenanceRecord.description, MaintenanceRecord.notes]

    query = db.query(MaintenanceRecord)

    # Search for the term in all specified fields
    if search_term:
        search_filters = []

        # Check if search_term is numeric to filter by maintenance_id
        if search_term.isdigit():
            search_filters.append(MaintenanceRecord.maintenance_id == int(search_term))

        # Apply ILIKE to string fields
        for field in search_fields:
            search_filters.append(field.ilike(f"%{search_term}%"))
        
        query = query.filter(or_(*search_filters))

    # Apply sorting
    if sort_order == 'asc':
        query = query.order_by(asc(getattr(MaintenanceRecord, sort_by)))
    else:
        query = query.order_by(desc(getattr(MaintenanceRecord, sort_by)))

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
