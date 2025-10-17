"""
Export Service for data export and report generation.
"""
import json
import csv
import io
from src.database import db
from src.models.student import Student
from src.models.learning_path import LearningPath
from src.models.student_session import StudentSession
from src.models.class_group import ClassGroup, ClassMembership
from src.services.analytics_dashboard_service import AnalyticsDashboardService
from datetime import datetime


class ExportService:
    """Service for data export and reporting"""
    
    @staticmethod
    def export_student_data(student_id, format='json'):
        """Export student data in specified format"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Get comprehensive student data
            dashboard_result, _ = AnalyticsDashboardService.get_student_dashboard(student_id, 30)
            
            if not dashboard_result.get('success'):
                return dashboard_result, 500
            
            # Get learning paths
            paths = LearningPath.query.filter_by(student_id=student_id).all()
            
            # Get recent sessions
            sessions = StudentSession.query.filter_by(student_id=student_id).order_by(
                StudentSession.started_at.desc()
            ).limit(50).all()
            
            data = {
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'grade': student.grade
                },
                'dashboard': dashboard_result['dashboard'],
                'learning_paths': [
                    {
                        'skill_id': p.skill_id,
                        'skill_name': p.skill.name if p.skill else 'Unknown',
                        'accuracy': round(p.current_accuracy * 100, 1),
                        'mastered': p.mastery_achieved,
                        'questions_answered': p.questions_answered
                    }
                    for p in paths
                ],
                'recent_sessions': [
                    {
                        'date': s.started_at.isoformat(),
                        'duration_minutes': round((s.ended_at - s.started_at).total_seconds() / 60, 1) if s.ended_at else 0,
                        'questions_answered': s.questions_answered,
                        'questions_correct': s.questions_correct,
                        'accuracy': round((s.questions_correct / s.questions_answered * 100), 1) if s.questions_answered > 0 else 0
                    }
                    for s in sessions
                ],
                'export_date': datetime.utcnow().isoformat()
            }
            
            if format == 'json':
                return {'success': True, 'data': data, 'format': 'json'}, 200
            
            elif format == 'csv':
                # Convert to CSV (flattened structure)
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Header
                writer.writerow(['Student Name', 'Grade', 'Total Time (min)', 'Total Sessions', 
                                'Avg Accuracy', 'Skills Mastered', 'Engagement Score'])
                
                # Data row
                dashboard = data['dashboard']['summary']
                writer.writerow([
                    data['student']['name'],
                    data['student']['grade'],
                    dashboard['total_time_minutes'],
                    dashboard['total_sessions'],
                    dashboard['average_accuracy'],
                    dashboard['skills_mastered'],
                    dashboard['engagement_score']
                ])
                
                csv_data = output.getvalue()
                return {'success': True, 'data': csv_data, 'format': 'csv'}, 200
            
            else:
                return {'success': False, 'error': 'Unsupported format'}, 400
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def export_class_data(class_id, format='json'):
        """Export class data in specified format"""
        try:
            class_group = ClassGroup.query.get(class_id)
            if not class_group:
                return {'success': False, 'error': 'Class not found'}, 404
            
            # Get class members
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            # Get data for each student
            students_data = []
            for student_id in student_ids:
                student = Student.query.get(student_id)
                if student:
                    dashboard_result, _ = AnalyticsDashboardService.get_student_dashboard(student_id, 30)
                    
                    if dashboard_result.get('success'):
                        summary = dashboard_result['dashboard']['summary']
                        students_data.append({
                            'student_id': student_id,
                            'student_name': student.name,
                            'total_time': summary['total_time_minutes'],
                            'total_sessions': summary['total_sessions'],
                            'average_accuracy': summary['average_accuracy'],
                            'skills_mastered': summary['skills_mastered'],
                            'engagement_score': summary['engagement_score']
                        })
            
            data = {
                'class': {
                    'id': class_group.id,
                    'name': class_group.name,
                    'grade_level': class_group.grade_level,
                    'student_count': len(students_data)
                },
                'students': students_data,
                'export_date': datetime.utcnow().isoformat()
            }
            
            if format == 'json':
                return {'success': True, 'data': data, 'format': 'json'}, 200
            
            elif format == 'csv':
                # Convert to CSV
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Header
                writer.writerow(['Student Name', 'Total Time (min)', 'Total Sessions', 
                                'Avg Accuracy', 'Skills Mastered', 'Engagement Score'])
                
                # Data rows
                for student in students_data:
                    writer.writerow([
                        student['student_name'],
                        student['total_time'],
                        student['total_sessions'],
                        student['average_accuracy'],
                        student['skills_mastered'],
                        student['engagement_score']
                    ])
                
                csv_data = output.getvalue()
                return {'success': True, 'data': csv_data, 'format': 'csv'}, 200
            
            else:
                return {'success': False, 'error': 'Unsupported format'}, 400
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def generate_report(report_type, entity_id, format='json'):
        """Generate a specific type of report"""
        try:
            if report_type == 'student_progress':
                return ExportService.export_student_data(entity_id, format)
            
            elif report_type == 'class_performance':
                return ExportService.export_class_data(entity_id, format)
            
            elif report_type == 'comparative':
                # Get comparative analytics
                from src.services.analytics_dashboard_service import AnalyticsDashboardService
                result, status = AnalyticsDashboardService.get_comparative_analytics(entity_id, 'class')
                
                if not result.get('success'):
                    return result, status
                
                if format == 'json':
                    return {'success': True, 'data': result['comparison'], 'format': 'json'}, 200
                else:
                    return {'success': False, 'error': 'CSV not supported for comparative reports'}, 400
            
            else:
                return {'success': False, 'error': 'Unknown report type'}, 400
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

