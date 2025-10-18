"""
Database configuration and initialization for Alpha Learning Platform.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Initialize Flask-Migrate instance
migrate = Migrate()


def init_db(app):
    """
    Initialize database with Flask app.
    
    Args:
        app: Flask application instance
    """
    # Configure database URI
    import os
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///alpha_learning.db')
    
    # Fix Railway's postgres:// to postgresql://
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return db
