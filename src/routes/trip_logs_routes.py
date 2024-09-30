import contextlib
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, String, asc, desc
from db.connection import SessionLocal
from models.trip_logs_model import TripLog
from models.vehicle_model import Vehicle
from services.trip_logs_services import (
    create_trip_log,
    get_trip_log,
    update_trip_log,
    delete_trip_log
)

# Blueprint for trip log routes
trip_log_bp = Blueprint('trip_log', __name__)

# Helper function to fetch the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Decorator to fetch DB session
def with_db(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with contextlib.closing(next(get_db())) as db:
            return f(db, *args, **kwargs)
    return decorated_function

# Helper function to return a not found response
def check_trip_log_not_found(trip_log):
    if not trip_log:
        return jsonify({'error': 'Trip log not found'}), 404

# Render the HTML form for creating a new trip log
@trip_log_bp.route('/trip_logs/new', methods=['GET'])
def new_trip_log_form():
    return render_template('trip_logs_create_form.html')

# Render the table display and search form HTML
@trip_log_bp.route('/trip_logs/search/form', methods=['GET'])
def trip_logs_table_form():
    return render_template('trip_logs_search_form.html')

# Render the update trip log form
@trip_log_bp.route('/trip_logs/<int:trip_id>/update', methods=['GET'])
@with_db
@jwt_required()
def update_trip_log_form(db, trip_id):
    trip_log = get_trip_log(db, trip_id=trip_id)
    not_found = check_trip_log_not_found(trip_log)
    if not_found:
        return not_found
    return render_template('trip_logs_update_form.html', trip_log=trip_log)

# Trip log creation endpoint
@trip_log_bp.route('/trip_logs', methods=['POST'])
@jwt_required()
def create_trip_log_endpoint():
    db = next(get_db())
    data = request.get_json()

    try:
        new_trip_log = create_trip_log(db, data)

        # Update vehicle mileage if mileage_end is provided
        if new_trip_log.mileage_end:
            vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == new_trip_log.vehicle_id).first()
            if vehicle:
                vehicle.mileage = new_trip_log.mileage_end
                db.commit()

        return jsonify(new_trip_log.to_dict()), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()

# Return a trip log by ID
@trip_log_bp.route('/trip_logs/<int:trip_id>', methods=['GET'])
@with_db
@jwt_required()
def get_trip_log_by_id_endpoint(db, trip_id):
    trip_log = get_trip_log(db, trip_id=trip_id)
    not_found = check_trip_log_not_found(trip_log)
    if not_found:
        return not_found
    return jsonify(trip_log.to_dict())

# Unified search, filtering, sorting, and pagination for trip logs
@trip_log_bp.route('/trip_logs/search', methods=['GET'])
@with_db
def search_trip_logs(db):
    search_term = request.args.get('query', '')
    sort_by = request.args.get('sortBy', 'trip_id')  # Default sort by trip ID
    sort_order = request.args.get('sortOrder', 'asc')  # Default sort order ascending

    # Attributes to search for both string and numeric fields
    search_fields = [TripLog.trip_id, TripLog.driver_id, TripLog.vehicle_id, TripLog.status]

    query = db.query(TripLog)

    # Search for the term in all specified fields
    if search_term:
        search_filters = []

        try:
            search_value = int(search_term)
            search_filters.append(TripLog.trip_id == search_value)
            search_filters.append(TripLog.vehicle_id == search_value)
            search_filters.append(TripLog.driver_id == search_value)
        except ValueError:
            pass  # Not numeric, continue to search string fields

        for field in search_fields:
            if isinstance(field.type, String):
                search_filters.append(field.ilike(f"%{search_term}%"))

        query = query.filter(or_(*search_filters))

    # Apply sorting
    query = query.order_by(asc(getattr(TripLog, sort_by))) if sort_order == 'asc' else query.order_by(desc(getattr(TripLog, sort_by)))

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    skip = (page - 1) * per_page

    trip_logs = query.offset(skip).limit(per_page).all()
    total_trip_logs = query.count()

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total_trip_logs': total_trip_logs,
        'trip_logs': [trip_log.to_dict() for trip_log in trip_logs]
    })

# Update trip log details
@trip_log_bp.route('/trip_logs/<int:trip_id>', methods=['PUT'])
@jwt_required()
def update_trip_log_endpoint(trip_id):
    db = next(get_db())
    data = request.get_json()

    try:
        updated_trip_log = update_trip_log(db, trip_id, data)
        not_found = check_trip_log_not_found(updated_trip_log)
        if not_found:
            return not_found

        # Update vehicle mileage if mileage_end is provided
        if updated_trip_log.mileage_end:
            vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == updated_trip_log.vehicle_id).first()
            if vehicle:
                vehicle.mileage = updated_trip_log.mileage_end
                db.commit()

        return jsonify(updated_trip_log.to_dict()), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()

# Delete a trip log
@trip_log_bp.route('/trip_logs/<int:trip_id>', methods=['DELETE'])
@with_db
def delete_trip_log_endpoint(db, trip_id):
    deleted_trip_log = delete_trip_log(db, trip_id=trip_id)
    not_found = check_trip_log_not_found(deleted_trip_log)
    if not_found:
        return not_found
    return jsonify({'message': 'Trip log deleted successfully'})