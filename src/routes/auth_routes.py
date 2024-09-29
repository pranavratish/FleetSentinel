from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required
from db.connection import SessionLocal
from models.user_model import User

auth_bp = Blueprint('auth', __name__)

# Route to render the registration page
@auth_bp.route('/register/form', methods=['GET'])
def register_form():
    return render_template('registration_form.html')

# Register a new user
@auth_bp.route('/register', methods=['POST'])
def register():
    db = SessionLocal()
    try:
        # Check if users exist in the database
        user_count = db.query(User).count()

        # If no users exist, allow the first user to register without requiring JWT
        if user_count == 0:
            return register_first_user(db)

        # For subsequent registrations, enforce JWT authentication
        return register_with_jwt(db)
    finally:
        db.close()


# Helper function for the first user registration (without JWT)
def register_first_user(db):
    db = SessionLocal()
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Check if user already exists
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # Create new user (give the first user admin privileges if needed)
        new_user = User(username=username, role='admin')  # Set role as 'admin'
        new_user.set_pass(password)
        db.add(new_user)
        db.commit()

        return jsonify({"message": "First user (admin) created successfully"}), 201
    finally:
        db.close()


# Helper function for registration with JWT (for all future users)
@jwt_required()
def register_with_jwt(db):
    db = SessionLocal()
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Check if user already exists
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # Create a regular user
        new_user = User(username=username, role='user')  # Default role for subsequent users
        new_user.set_pass(password)
        db.add(new_user)
        db.commit()

        return jsonify({"message": "User created successfully"}), 201
    finally:
        db.close()


# Login a user and generate a JWT
@auth_bp.route('/login', methods=['POST'])
def login():
    db = SessionLocal()
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = db.query(User).filter_by(username=username).first()

        if user is None or not user.check_pass(password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Create a new access token
        access_token = create_access_token(identity={'username': user.username, 'role': user.role})
        return jsonify(access_token=access_token), 200
    finally:
        db.close()