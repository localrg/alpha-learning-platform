"""
Security configuration and hardening for Alpha Learning Platform.
Implements security best practices for production deployment.
"""
from flask import Flask, request, abort
from functools import wraps
import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class SecurityConfig:
    """Security configuration and hardening"""
    
    # Password policy
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Account lockout
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # Session security
    SESSION_TIMEOUT_MINUTES = 60
    ABSOLUTE_SESSION_TIMEOUT_HOURS = 12
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    
    # File upload security
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FILE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'}
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }


def configure_security(app: Flask):
    """Configure security middleware and headers"""
    
    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response
    
    # Remove server header
    @app.after_request
    def remove_server_header(response):
        response.headers.pop('Server', None)
        return response
    
    # HTTPS redirect in production
    @app.before_request
    def https_redirect():
        if app.config.get('ENV') == 'production':
            if not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)
    
    print("✓ Security configuration applied")


class PasswordValidator:
    """Validate passwords against security policy"""
    
    @staticmethod
    def validate(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password against security policy.
        Returns (is_valid, error_message)
        """
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters"
        
        if SecurityConfig.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if SecurityConfig.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if SecurityConfig.REQUIRE_NUMBERS and not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        from werkzeug.security import generate_password_hash
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        from werkzeug.security import check_password_hash
        return check_password_hash(password_hash, password)


class AccountLockout:
    """Track and enforce account lockout policy"""
    
    # In-memory storage (use Redis in production)
    failed_attempts: Dict[str, List[datetime]] = {}
    locked_accounts: Dict[str, datetime] = {}
    
    @classmethod
    def record_failed_attempt(cls, username: str):
        """Record a failed login attempt"""
        now = datetime.now()
        
        if username not in cls.failed_attempts:
            cls.failed_attempts[username] = []
        
        # Add current attempt
        cls.failed_attempts[username].append(now)
        
        # Remove attempts older than lockout duration
        cutoff = now - timedelta(minutes=SecurityConfig.LOCKOUT_DURATION_MINUTES)
        cls.failed_attempts[username] = [
            attempt for attempt in cls.failed_attempts[username]
            if attempt > cutoff
        ]
        
        # Check if account should be locked
        if len(cls.failed_attempts[username]) >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
            cls.locked_accounts[username] = now
    
    @classmethod
    def is_locked(cls, username: str) -> bool:
        """Check if account is currently locked"""
        if username not in cls.locked_accounts:
            return False
        
        locked_at = cls.locked_accounts[username]
        unlock_time = locked_at + timedelta(minutes=SecurityConfig.LOCKOUT_DURATION_MINUTES)
        
        if datetime.now() < unlock_time:
            return True
        else:
            # Unlock account
            del cls.locked_accounts[username]
            cls.failed_attempts[username] = []
            return False
    
    @classmethod
    def reset_attempts(cls, username: str):
        """Reset failed attempts after successful login"""
        cls.failed_attempts.pop(username, None)
        cls.locked_accounts.pop(username, None)


class InputSanitizer:
    """Sanitize user inputs to prevent injection attacks"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return ""
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Trim to max length
        value = value[:max_length]
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def sanitize_email(email: str) -> Optional[str]:
        """Validate and sanitize email address"""
        email = InputSanitizer.sanitize_string(email, 255)
        
        # Basic email regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_regex, email):
            return email.lower()
        return None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Limit length
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:200]
        
        return f"{name}.{ext}" if ext else name


class RateLimiter:
    """Rate limiting to prevent abuse"""
    
    # In-memory storage (use Redis in production)
    requests: Dict[str, List[datetime]] = {}
    
    @classmethod
    def check_rate_limit(cls, identifier: str, limit: int, window_minutes: int) -> bool:
        """
        Check if request is within rate limit.
        Returns True if allowed, False if rate limit exceeded.
        """
        now = datetime.now()
        
        if identifier not in cls.requests:
            cls.requests[identifier] = []
        
        # Remove old requests outside the window
        cutoff = now - timedelta(minutes=window_minutes)
        cls.requests[identifier] = [
            req_time for req_time in cls.requests[identifier]
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(cls.requests[identifier]) >= limit:
            return False
        
        # Add current request
        cls.requests[identifier].append(now)
        return True
    
    @classmethod
    def rate_limit_decorator(cls, limit: int = 60, window_minutes: int = 1):
        """Decorator for rate limiting endpoints"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Use IP address as identifier
                identifier = request.remote_addr
                
                if not cls.check_rate_limit(identifier, limit, window_minutes):
                    abort(429, description="Rate limit exceeded. Please try again later.")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator


class FileUploadSecurity:
    """Secure file upload handling"""
    
    @staticmethod
    def validate_file(file, allowed_extensions: set = None) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded file.
        Returns (is_valid, error_message)
        """
        if allowed_extensions is None:
            allowed_extensions = SecurityConfig.ALLOWED_FILE_EXTENSIONS
        
        # Check if file exists
        if not file or not file.filename:
            return False, "No file provided"
        
        # Check file extension
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size = SecurityConfig.MAX_FILE_SIZE_MB * 1024 * 1024
        if size > max_size:
            return False, f"File too large. Maximum size: {SecurityConfig.MAX_FILE_SIZE_MB}MB"
        
        return True, None
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Generate secure filename with random component"""
        # Sanitize original filename
        safe_name = InputSanitizer.sanitize_filename(original_filename)
        
        # Add random component
        random_component = secrets.token_hex(8)
        
        # Combine with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        name, ext = safe_name.rsplit('.', 1) if '.' in safe_name else (safe_name, '')
        
        return f"{name}_{timestamp}_{random_component}.{ext}" if ext else f"{name}_{timestamp}_{random_component}"


class CSRFProtection:
    """CSRF token generation and validation"""
    
    @staticmethod
    def generate_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_token(token: str, session_token: str) -> bool:
        """Validate CSRF token"""
        return secrets.compare_digest(token, session_token)


# Security utilities
def get_client_ip() -> str:
    """Get client IP address, considering proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def hash_data(data: str) -> str:
    """Hash data using SHA-256"""
    return hashlib.sha256(data.encode()).hexdigest()


# Security statistics
def get_security_stats():
    """Get security configuration statistics"""
    return {
        'password_policy': {
            'min_length': SecurityConfig.MIN_PASSWORD_LENGTH,
            'requires_uppercase': SecurityConfig.REQUIRE_UPPERCASE,
            'requires_lowercase': SecurityConfig.REQUIRE_LOWERCASE,
            'requires_numbers': SecurityConfig.REQUIRE_NUMBERS,
            'requires_special_chars': SecurityConfig.REQUIRE_SPECIAL_CHARS
        },
        'account_lockout': {
            'max_attempts': SecurityConfig.MAX_LOGIN_ATTEMPTS,
            'lockout_duration_minutes': SecurityConfig.LOCKOUT_DURATION_MINUTES
        },
        'rate_limiting': {
            'per_minute': SecurityConfig.RATE_LIMIT_PER_MINUTE,
            'per_hour': SecurityConfig.RATE_LIMIT_PER_HOUR
        },
        'file_upload': {
            'max_size_mb': SecurityConfig.MAX_FILE_SIZE_MB,
            'allowed_extensions': list(SecurityConfig.ALLOWED_FILE_EXTENSIONS)
        },
        'security_headers': len(SecurityConfig.SECURITY_HEADERS)
    }


if __name__ == '__main__':
    import json
    stats = get_security_stats()
    print("Security Configuration:")
    print(json.dumps(stats, indent=2))

