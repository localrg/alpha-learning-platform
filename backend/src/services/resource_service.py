"""
Resource Service for managing educational resources.
"""
from src.database import db
from src.models.resource import Resource, ResourceDownload
from sqlalchemy import or_, and_


class ResourceService:
    """Service for managing educational resources."""

    @staticmethod
    def get_all_resources(filters=None):
        """
        Get all resources with optional filters.
        
        Filters:
        - resource_type: Filter by type
        - skill_id: Filter by skill
        - grade_level: Filter by grade
        - difficulty: Filter by difficulty
        - search: Search in title, description, tags
        """
        query = Resource.query.filter_by(is_active=True)
        
        if filters:
            # Filter by resource type
            if filters.get('resource_type'):
                query = query.filter_by(resource_type=filters['resource_type'])
            
            # Filter by skill
            if filters.get('skill_id'):
                query = query.filter_by(skill_id=filters['skill_id'])
            
            # Filter by grade level
            if filters.get('grade_level'):
                query = query.filter_by(grade_level=filters['grade_level'])
            
            # Filter by difficulty
            if filters.get('difficulty'):
                query = query.filter_by(difficulty=filters['difficulty'])
            
            # Search in title, description, tags
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Resource.title.ilike(search_term),
                        Resource.description.ilike(search_term)
                    )
                )
        
        # Order by newest first
        query = query.order_by(Resource.created_at.desc())
        
        return query.all()

    @staticmethod
    def get_resource_by_id(resource_id):
        """Get a resource by ID."""
        resource = Resource.query.get(resource_id)
        return resource.to_dict() if resource else None

    @staticmethod
    def get_related_resources(resource_id, limit=5):
        """Get related resources based on skill and grade level."""
        resource = Resource.query.get(resource_id)
        if not resource:
            return []
        
        # Find resources with same skill or grade level
        related = Resource.query.filter(
            and_(
                Resource.id != resource_id,
                Resource.is_active == True,
                or_(
                    Resource.skill_id == resource.skill_id,
                    Resource.grade_level == resource.grade_level
                )
            )
        ).limit(limit).all()
        
        return [r.to_dict() for r in related]

    @staticmethod
    def create_resource(resource_data):
        """Create a new resource."""
        resource = Resource(
            title=resource_data.get('title'),
            description=resource_data.get('description'),
            resource_type=resource_data.get('resource_type'),
            skill_id=resource_data.get('skill_id'),
            grade_level=resource_data.get('grade_level'),
            difficulty=resource_data.get('difficulty', 'medium'),
            file_url=resource_data.get('file_url'),
            file_type=resource_data.get('file_type'),
            file_size_kb=resource_data.get('file_size_kb'),
            thumbnail_url=resource_data.get('thumbnail_url'),
            tags=resource_data.get('tags', [])
        )
        
        db.session.add(resource)
        db.session.commit()
        
        return resource

    @staticmethod
    def update_resource(resource_id, resource_data):
        """Update an existing resource."""
        resource = Resource.query.get(resource_id)
        if not resource:
            return None
        
        # Update fields
        if 'title' in resource_data:
            resource.title = resource_data['title']
        if 'description' in resource_data:
            resource.description = resource_data['description']
        if 'resource_type' in resource_data:
            resource.resource_type = resource_data['resource_type']
        if 'skill_id' in resource_data:
            resource.skill_id = resource_data['skill_id']
        if 'grade_level' in resource_data:
            resource.grade_level = resource_data['grade_level']
        if 'difficulty' in resource_data:
            resource.difficulty = resource_data['difficulty']
        if 'tags' in resource_data:
            resource.tags = resource_data['tags']
        if 'is_active' in resource_data:
            resource.is_active = resource_data['is_active']
        
        db.session.commit()
        
        return resource

    @staticmethod
    def delete_resource(resource_id):
        """Soft delete a resource (set is_active to False)."""
        resource = Resource.query.get(resource_id)
        if not resource:
            return False
        
        resource.is_active = False
        db.session.commit()
        
        return True

    @staticmethod
    def record_download(student_id, resource_id, download_method='direct'):
        """Record that a student downloaded a resource."""
        # Create download record
        download = ResourceDownload(
            student_id=student_id,
            resource_id=resource_id,
            download_method=download_method
        )
        
        db.session.add(download)
        
        # Increment download count
        resource = Resource.query.get(resource_id)
        if resource:
            resource.download_count += 1
        
        db.session.commit()
        
        return download

    @staticmethod
    def get_student_downloads(student_id, limit=None):
        """Get download history for a student."""
        query = ResourceDownload.query.filter_by(student_id=student_id).order_by(
            ResourceDownload.downloaded_at.desc()
        )
        
        if limit:
            query = query.limit(limit)
        
        downloads = query.all()
        return [d.to_dict() for d in downloads]

    @staticmethod
    def get_resource_stats(resource_id):
        """Get statistics for a resource."""
        downloads = ResourceDownload.query.filter_by(resource_id=resource_id).all()
        
        if not downloads:
            return {
                'total_downloads': 0,
                'unique_students': 0,
                'downloads_by_method': {},
                'downloads_last_30_days': 0
            }
        
        # Count unique students
        unique_students = len(set(d.student_id for d in downloads))
        
        # Count by method
        downloads_by_method = {}
        for download in downloads:
            method = download.download_method
            downloads_by_method[method] = downloads_by_method.get(method, 0) + 1
        
        # Count last 30 days
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        downloads_last_30_days = sum(
            1 for d in downloads if d.downloaded_at >= thirty_days_ago
        )
        
        return {
            'total_downloads': len(downloads),
            'unique_students': unique_students,
            'downloads_by_method': downloads_by_method,
            'downloads_last_30_days': downloads_last_30_days
        }

    @staticmethod
    def get_available_filters():
        """Get available filter options based on current resources."""
        resources = Resource.query.filter_by(is_active=True).all()
        
        types = list(set(r.resource_type for r in resources))
        grades = sorted(list(set(r.grade_level for r in resources)))
        difficulties = list(set(r.difficulty for r in resources))
        
        return {
            'types': types,
            'grades': grades,
            'difficulties': difficulties
        }

    @staticmethod
    def get_popular_resources(limit=10):
        """Get most downloaded resources."""
        resources = Resource.query.filter_by(is_active=True).order_by(
            Resource.download_count.desc()
        ).limit(limit).all()
        
        return [r.to_dict() for r in resources]

    @staticmethod
    def get_recent_resources(limit=10):
        """Get recently added resources."""
        resources = Resource.query.filter_by(is_active=True).order_by(
            Resource.created_at.desc()
        ).limit(limit).all()
        
        return [r.to_dict() for r in resources]

