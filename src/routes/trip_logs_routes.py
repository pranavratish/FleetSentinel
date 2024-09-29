import json
import contextlib
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, current_app
from sqlalchemy import or_, String
from db.connection import SessionLocal
from models.trip_logs_model import TripLog
from models.vehicle_model import Vehicle
from services.filtering_services import filter_records
from services.trip_logs_services import (
    create_trip_log,
    get_trip_log,
    update_trip_log,
    delete_trip_log
)

# declares Blueprint for trip log routes
trip_log_bp = Blueprint('trip_log', __name__)

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

# Helper function to log "Trip log not found" case
def trip_log_not_found_response(trip_log):
    if not trip_log:
        return jsonify({'error': 'Trip log not found'}), 404

# Serves the HTML form for creating a new trip log
@trip_log_bp.route('/trip_logs/new', methods=['GET'])
def new_trip_log_form():
    return render_template('trip_logs_create_form.html')

# Renders the table display and search form HTML file
@trip_log_bp.route('/trip_logs/search/form', methods=['GET'])
def trip_logs_table_form():
    return render_template('trip_logs_search_form.html')

# Renders the update trip log HTML form
@trip_log_bp.route('/trip_logs/<int:trip_id>/update', methods=['GET'])
@with_db
def update_trip_log_form(db, trip_id):
    trip_log = get_trip_log(db, trip_id=trip_id)  
    if not trip_log:
        current_app.logger.error(f"Trip log with ID {trip_id} not found")
        return jsonify({'error': 'Trip log not found'}), 404
    return render_template('trip_logs_update_form.html', trip_log=trip_log)

# Trip log creation endpoint
@trip_log_bp.route('/trip_logs', methods=['POST'])
def create_trip_log():
    db = next(get_db())
    data = request.get_json()

    try:
        # Create the trip log
        new_trip = TripLog(**data)
        db.add(new_trip)
        db.commit()
        db.refresh(new_trip)

        # Update the vehicle's mileage if mileage_end is provided
        if new_trip.mileage_end:
            vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == new_trip.vehicle_id).first()
            if vehicle:
                vehicle.mileage = new_trip.mileage_end
                db.commit()

        return jsonify(new_trip.to_dict()), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()

# returns a trip log by ID
@trip_log_bp.route('/trip_logs/<int:trip_id>', methods=['GET'])
@with_db
def get_trip_log_by_id_endpoint(db, trip_id):
    trip_log = get_trip_log(db, trip_id=trip_id)
    not_found = trip_log_not_found_response(trip_log)
    if not_found:
        return not_found
    return jsonify(trip_log.to_dict())

# more accessible search function and table display of rows with pagination
@trip_log_bp.route('/trip_logs/search', methods=['GET'])
@with_db
def search_trip_logs(db):
    search_term = request.args.get('query', '')

    # List of attributes to search
    search_fields = [TripLog.trip_id, TripLog.driver_id, TripLog.vehicle_id, TripLog.status]

    query = db.query(TripLog)

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

    trip_logs = query.offset(skip).limit(per_page).all()
    total_trip_logs = query.count()

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total_trip_logs': total_trip_logs,
        'trip_logs': [trip_log.to_dict() for trip_log in trip_logs]
    })

@trip_log_bp.route('/trip_logs', methods=['GET'])
def get_filtered_sorted_trips():
    db = SessionLocal()
    
    # Get filters and sorting parameters from the request
    filters = request.args.get('filters', '{}')
    sort = request.args.get('sort', '{}')
    
    # Convert JSON strings into Python dictionaries
    filter_params = json.loads(filters)
    sort_params = json.loads(sort)
    
    query = db.query(TripLog)
    
    # Apply filtering and sorting
    query = filter_records(query, filter_params, sort_params, TripLog)
    
    # Execute the query and return results
    trips = query.all()
    return jsonify([trip.to_dict() for trip in trips])

# updates a trip log's details (supports partial updates)
@trip_log_bp.route('/trip_logs/<int:trip_id>', methods=['PUT'])
def update_trip_log(trip_id):
    db = next(get_db())
    data = request.get_json()

    try:
        # Find the trip log
        trip_log = db.query(TripLog).filter(TripLog.trip_id == trip_id).first()
        if not trip_log:
            return jsonify({'error': 'Trip log not found'}), 404

        # Update the trip log fields
        for key, value in data.items():
            setattr(trip_log, key, value)
        
        db.commit()

        # Update the vehicle's mileage if mileage_end is provided
        if trip_log.mileage_end:
            vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == trip_log.vehicle_id).first()
            if vehicle:
                vehicle.mileage = trip_log.mileage_end
                db.commit()

        return jsonify(trip_log.to_dict()), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()

# deletes a trip log
@trip_log_bp.route('/trip_logs/<int:trip_id>', methods=['DELETE'])
@with_db
def delete_trip_log_endpoint(db, trip_id):
    deleted_trip_log = delete_trip_log(db, trip_id=trip_id)
    not_found = trip_log_not_found_response(deleted_trip_log)
    if not_found:
        return not_found
    return jsonify({'message': 'Trip log deleted successfully'})