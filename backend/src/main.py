"""
Main application entry point for Alpha Learning Platform.
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database initialization
from src.database.database import init_db

# Import route blueprints
from src.routes.auth import auth_bp
from src.routes.student_routes import student_bp
from src.routes.teacher_routes import teacher_bp
from src.routes.parent_routes import parent_bp
from src.routes.admin_routes import admin_bp
from src.routes.shared_challenge_routes import shared_challenge_bp
from src.routes.activity_feed_routes import activity_feed_bp

# Create Flask application
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

# Initialize database
db = init_db(app)

# Register blueprints with /api prefix
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
    """Root endpoint"""
    return {
        'message': 'Alpha Learning Platform API',
        'version': '1.0',
        'status': 'running'
    }, 200

# API root route
@app.route('/api')
@app.route('/api/')
def api_root():
    """API root endpoint"""
    return {
        'message': 'Alpha Learning Platform API',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            'auth': '/api/auth',
            'student': '/api/student',
            'teacher': '/api/teacher',
            'parent': '/api/parent',
            'admin': '/api/admin',
            'challenges': '/api/challenges',
            'activity': '/api/activity'
        }
    }, 200

# Export app for Gunicorn
# Note: No app.run() here - Gunicorn handles that
