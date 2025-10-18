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
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'database', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///alpha_learning.db')'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return db

