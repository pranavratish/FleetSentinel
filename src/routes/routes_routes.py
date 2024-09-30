import contextlib
from functools import wraps
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, String, asc, desc
from db.connection import SessionLocal
from models.routes_model import Route
from services.routes_services import (
    create_route,
    get_route,
    update_route,
    delete_route
)

# declares Blueprint for route routes
route_bp = Blueprint('route', __name__)

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

# General helper function to handle "Not found" cases for any entity
def not_found(entity, entity_name="Entity"):
    if not entity:
        return jsonify({'error': f'{entity_name} not found'}), 404

# serves the HTML form for creating a new route
@route_bp.route('/routes/new', methods=['GET'])
def new_route_form():
    return render_template('route_create_form.html')

# serves the HTML form for searching/displaying the existing routes
@route_bp.route('/routes/search/form', methods=['GET'])
def search_routes_form():
    return render_template('route_search_form.html')

# renders the HTML form for updating an existing route and preloads the route data
@route_bp.route('/routes/<int:route_id>/update', methods=['GET'])
@with_db
@jwt_required()
def update_route_form(db, route_id):
    route = get_route(db, route_id=route_id)
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    return render_template('route_update_form.html', route=route)

# creates a new route
@route_bp.route('/routes', methods=['POST'])
@with_db
@jwt_required()
def create_route_endpoint(db):
    data = request.get_json()
    new_route = create_route(db, data)
    return jsonify(new_route.to_dict()), 201

# returns a route by ID
@route_bp.route('/routes/<int:route_id>', methods=['GET'])
@with_db
@jwt_required()
def get_route_by_id_endpoint(db, route_id):
    route = get_route(db, route_id=route_id)
    return not_found(route, "Route") or jsonify(route.to_dict())

# updates a route's details (supports partial updates)
@route_bp.route('/routes/<int:route_id>', methods=['PUT'])
@with_db
@jwt_required()
def update_route_endpoint(db, route_id):
    data = request.get_json()
    updated_route = update_route(db, route_id=route_id, data=data)
    return not_found(updated_route, "Route") or jsonify(updated_route.to_dict())

# deletes a route
@route_bp.route('/routes/<int:route_id>', methods=['DELETE'])
@with_db
@jwt_required()
def delete_route_endpoint(db, route_id):
    deleted_route = delete_route(db, route_id=route_id)
    return not_found(deleted_route, "Route") or jsonify({'message': 'Route deleted successfully'})

# more accessible search, filtering, sorting, and table display of rows with pagination
@route_bp.route('/routes/search', methods=['GET'])
@with_db
def search_routes(db):
    search_term = request.args.get('query', '')
    sort_by = request.args.get('sortBy', 'route_id')  # Default sort by route ID
    sort_order = request.args.get('sortOrder', 'asc')  # Default sort order ascending

    # List of attributes to search for string fields
    search_fields = [Route.origin, Route.destination]

    query = db.query(Route)

    # Search for the term in all specified fields
    if search_term:
        search_filters = []

        # Check if the search term is numeric to filter by route_id
        if search_term.isdigit():
            search_filters.append(Route.route_id == int(search_term))

        # Apply ILIKE for string fields
        for field in search_fields:
            search_filters.append(field.ilike(f"%{search_term}%"))
        
        query = query.filter(or_(*search_filters))

    # Apply sorting
    if sort_order == 'asc':
        query = query.order_by(asc(getattr(Route, sort_by)))
    else:
        query = query.order_by(desc(getattr(Route, sort_by)))

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    skip = (page - 1) * per_page

    routes = query.offset(skip).limit(per_page).all()
    total_routes = query.count()

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total_routes': total_routes,
        'routes': [route.to_dict() for route in routes]
    })