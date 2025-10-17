import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.database import init_db
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

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production-2024'  # Change this in production!

# Initialize JWT
jwt = JWTManager(app)

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(assessment_bp, url_prefix='/api/assessment')
app.register_blueprint(learning_path_bp)
app.register_blueprint(review_bp)
app.register_blueprint(video_bp)
app.register_blueprint(example_bp)
app.register_blueprint(hint_bp)
app.register_blueprint(solution_bp)
app.register_blueprint(resource_bp)
app.register_blueprint(gamification_bp)
app.register_blueprint(achievement_routes_bp)
app.register_blueprint(leaderboard_bp)
app.register_blueprint(challenge_bp)
app.register_blueprint(streak_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(friend_bp)
app.register_blueprint(class_bp)
app.register_blueprint(shared_challenge_bp)
app.register_blueprint(activity_feed_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(assignment_routes_bp)
app.register_blueprint(monitoring_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(intervention_bp)
app.register_blueprint(parent_bp)
app.register_blueprint(parent_view_bp)
app.register_blueprint(report_bp)
app.register_blueprint(communication_bp)
app.register_blueprint(goal_bp)
app.register_blueprint(analytics_dashboard_bp)
app.register_blueprint(predictive_bp)
app.register_blueprint(recommendation_bp)
app.register_blueprint(export_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(init_bp)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Initialize database with test users on first run
    from init_db import init_database
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)

