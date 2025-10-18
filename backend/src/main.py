"""
Main application entry point for Alpha Learning Platform.
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask application first
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize database (import after app is created)
from database import init_db
db = init_db(app)

# Import route blueprints (after database is initialized)
from routes.auth import auth_bp
from routes.student_routes import student_bp
from routes.teacher_routes import teacher_bp
from routes.parent_routes import parent_bp
from routes.admin_routes import admin_bp
from routes.shared_challenge_routes import shared_challenge_bp
from routes.activity_feed_routes import activity_feed_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
app.register_blueprint(parent_bp, url_prefix='/api/parent')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(shared_challenge_bp, url_prefix='/api/challenges')
app.register_blueprint(activity_feed_bp, url_prefix='/api/activity')

# Root route
@app.route('/')
def index():
    return {'message': 'Alpha Learning Platform API', 'status': 'running'}, 200

# API root
@app.route('/api')
@app.route('/api/')
def api_root():
    return {
        'message': 'Alpha Learning Platform API',
        'version': '1.0',
        'status': 'running'
    }, 200
