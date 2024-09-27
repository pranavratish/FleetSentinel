import contextlib
from functools import wraps
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import or_, String
from db.connection import SessionLocal
from models.trip_logs_model import TripLog
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

# helper function to handle "Trip log not found" case
def trip_log_not_found_response(trip_log):
    if not trip_log:
        return jsonify({'error': 'Trip log not found'}), 404

# serves the HTML form for creating a new trip log
@trip_log_bp.route('/trip_logs/new', methods=['GET'])
def new_trip_log_form():
    return render_template('trip_log_create_form.html')

# renders the table display and search form HTML file
@trip_log_bp.route('/trip_logs/search/form', methods=['GET'])
def trip_logs_table_form():
    return render_template('trip_log_search_form.html')

# renders the update trip log HTML form
@trip_log_bp.route('/trip_logs/<int:trip_id>/update', methods=['GET'])
def update_trip_log_form(trip_id):
    return render_template('trip_log_update_form.html')

# creates a new trip log
@trip_log_bp.route('/trip_logs', methods=['POST'])
@with_db
def create_trip_log_endpoint(db):
    data = request.get_json()
    new_trip_log = create_trip_log(db, data)
    return jsonify(new_trip_log.to_dict()), 201

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
    search_fields = [TripLog.start_location, TripLog.end_location, TripLog.status]

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

# updates a trip log's details (supports partial updates)
@trip_log_bp.route('/trip_logs/<int:trip_id>', methods=['PUT'])
@with_db
def update_trip_log_endpoint(db, trip_id):
    # Get the data from the request
    data = request.get_json()

    # Call the update_trip_log function from the service
    updated_trip_log = update_trip_log(db, trip_id=trip_id, data=data)

    # If the trip log doesn't exist, handle the "not found" case
    not_found = trip_log_not_found_response(updated_trip_log)
    if not_found:
        return not_found

    # Return the updated trip log as a JSON response
    return jsonify(updated_trip_log.to_dict())

# deletes a trip log
@trip_log_bp.route('/trip_logs/<int:trip_id>', methods=['DELETE'])
@with_db
def delete_trip_log_endpoint(db, trip_id):
    deleted_trip_log = delete_trip_log(db, trip_id=trip_id)
    not_found = trip_log_not_found_response(deleted_trip_log)
    if not_found:
        return not_found
    return jsonify({'message': 'Trip log deleted successfully'})