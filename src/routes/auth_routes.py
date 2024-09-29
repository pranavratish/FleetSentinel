from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from db.connection import SessionLocal
from models.user_model import User

auth_bp = Blueprint('auth', __name__)

# Register a new user
@auth_bp.route('/register', methods=['POST'])
def register():
    db = SessionLocal()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if user already exists
    existing_user = db.query(User).filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # Create new user
    new_user = User(username=username)
    new_user.set_pass(password)
    db.add(new_user)
    db.commit()

    return jsonify({"message": "User created successfully"}), 201

# Login a user and generate a JWT
@auth_bp.route('/login', methods=['POST'])
def login():
    db = SessionLocal()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db.query(User).filter_by(username=username).first()

    if user is None or not user.check_pass(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create a new access token
    access_token = create_access_token(identity={'username': user.username})
    return jsonify(access_token=access_token), 200
