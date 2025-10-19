"""
Alpha Learning Platform - Main Application Entry Point
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database initialization
from src.database import init_db

# Import all models to ensure they're registered with SQLAlchemy
from src.models.user import User
from src.models.student import Student
from src.models.assessment import Assessment, AssessmentResponse, Question, Skill
from src.models.learning_path import LearningPath
from src.models.review import ReviewSession
from src.models.video import VideoTutorial, VideoView
from src.models.interactive_example import InteractiveExample, ExampleInteraction
from src.models.hint import Hint, HintUsage
from src.models.solution import WorkedSolution, SolutionView
from src.models.resource import Resource, ResourceDownload
from src.models.gamification import StudentProgress, XPTransaction, LevelReward, StudentReward
from src.models.achievement import Achievement, StudentAchievement, AchievementProgressLog
from src.models.daily_challenge import DailyChallenge
from src.models.streak import StreakTracking
from src.models.friendship import Friendship
from src.models.class_group import ClassGroup, ClassMembership
from src.models.shared_challenge import SharedChallenge, ChallengeParticipant
from src.models.activity_feed import ActivityFeed
from src.models.teacher import Teacher
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.student_session import StudentSession
from src.models.intervention import TeacherMessage, MessageTemplate, Intervention, Meeting
from src.models.parent import Parent, ParentChildLink, LinkRequest
from src.models.parent_communication import ParentTeacherMessage, Goal, GoalNote, GoalProgress
from src.models.admin_models import AuditLog, SystemSetting

# Import all route blueprints
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.student import student_bp
from src.routes.assessment import assessment_bp
from src.routes.learning_path import learning_path_bp
from src.routes.review import bp as review_bp
from src.routes.video import bp as video_bp
from src.routes.example import bp as example_bp
from src.routes.hint import hint_bp
from src.routes.solution import solution_bp
from src.routes.resource import resource_bp
from src.routes.gamification import gamification_bp
from src.routes.achievement_routes import achievement_routes_bp
from src.routes.leaderboard_routes import leaderboard_bp
from src.routes.challenge_routes import challenge_bp
from src.routes.streak_routes import streak_bp
from src.routes.profile_routes import profile_bp
from src.routes.friend_routes import friend_bp
from src.routes.class_routes import class_bp
from src.routes.shared_challenge_routes import shared_challenge_bp
from src.routes.activity_feed_routes import activity_feed_bp
from src.routes.teacher_routes import teacher_bp
from src.routes.assignment_routes import assignment_routes_bp
from src.routes.monitoring_routes import monitoring_bp
from src.routes.analytics_routes import analytics_bp
from src.routes.intervention_routes import intervention_bp
from src.routes.parent_routes import parent_bp
from src.routes.parent_view_routes import parent_view_bp
from src.routes.report_routes import report_bp
from src.routes.communication_routes import communication_bp
from src.routes.goal_routes import goal_bp
from src.routes.analytics_dashboard_routes import analytics_dashboard_bp
from src.routes.predictive_routes import predictive_bp
from src.routes.recommendation_routes import recommendation_bp
from src.routes.export_routes import export_bp
from src.routes.admin_routes import admin_bp
from src.routes.init_routes import init_bp

# Create Flask application
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Application configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours

# Initialize JWT
jwt = JWTManager(app)

# Initialize database
db = init_db(app)

# Register all blueprints with /api prefix
app.register_blueprint(init_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(student_bp, url_prefix='/api/students')
app.register_blueprint(assessment_bp, url_prefix='/api/assessments')
app.register_blueprint(learning_path_bp, url_prefix='/api/learning-paths')
app.register_blueprint(review_bp, url_prefix='/api/reviews')
app.register_blueprint(video_bp, url_prefix='/api/videos')
app.register_blueprint(example_bp, url_prefix='/api/examples')
app.register_blueprint(hint_bp, url_prefix='/api/hints')
app.register_blueprint(solution_bp, url_prefix='/api/solutions')
app.register_blueprint(resource_bp, url_prefix='/api/resources')
app.register_blueprint(gamification_bp, url_prefix='/api/gamification')
app.register_blueprint(achievement_routes_bp, url_prefix='/api/achievements')
app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')
app.register_blueprint(challenge_bp, url_prefix='/api/challenges')
app.register_blueprint(streak_bp, url_prefix='/api/streaks')
app.register_blueprint(profile_bp, url_prefix='/api/profile')
app.register_blueprint(friend_bp, url_prefix='/api/friends')
app.register_blueprint(class_bp, url_prefix='/api/classes')
app.register_blueprint(shared_challenge_bp, url_prefix='/api/shared-challenges')
app.register_blueprint(activity_feed_bp, url_prefix='/api/activity')
app.register_blueprint(teacher_bp, url_prefix='/api/teachers')
app.register_blueprint(assignment_routes_bp, url_prefix='/api/assignments')
app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(intervention_bp, url_prefix='/api/interventions')
app.register_blueprint(parent_bp, url_prefix='/api/parents')
app.register_blueprint(parent_view_bp, url_prefix='/api/parent-view')
app.register_blueprint(report_bp, url_prefix='/api/reports')
app.register_blueprint(communication_bp, url_prefix='/api/communication')
app.register_blueprint(goal_bp, url_prefix='/api/goals')
app.register_blueprint(analytics_dashboard_bp, url_prefix='/api/analytics-dashboard')
app.register_blueprint(predictive_bp, url_prefix='/api/predictive')
app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')
app.register_blueprint(export_bp, url_prefix='/api/export')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Root endpoint
@app.route('/')
def index():
    """Root endpoint - API health check"""
    return jsonify({
        'status': 'running',
        'message': 'Alpha Learning Platform API',
        'version': '1.0.0'
    })

# API info endpoint
@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'Alpha Learning Platform API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'students': '/api/students',
            'assessments': '/api/assessments',
            'teachers': '/api/teachers',
            'parents': '/api/parents',
            'admin': '/api/admin'
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Run application
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

