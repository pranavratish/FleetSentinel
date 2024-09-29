import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from routes.vehicle_routes import vehicle_bp
from routes.driver_routes import driver_bp
from routes.trip_logs_routes import trip_log_bp
from routes.routes_routes import route_bp
from routes.m_records_routes import maintenance_bp

# load env variables
load_dotenv()

app = Flask(__name__)

# setting secret key for JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

# registers blueprint for vehicles endpoints
app.register_blueprint(vehicle_bp)

# registers blueprint for drivers endpoints
app.register_blueprint(driver_bp)

# registers blueprint for trip logs endpoints
app.register_blueprint(trip_log_bp)

# registers blueprint for route endpoints
app.register_blueprint(route_bp)

# register blueprint for maintenance endpoints
app.register_blueprint(maintenance_bp)

# home page route
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)