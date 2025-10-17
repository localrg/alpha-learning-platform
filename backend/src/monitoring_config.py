"""
Monitoring and logging configuration for Alpha Learning Platform.
Implements comprehensive monitoring, logging, and alerting for production.
"""
import logging
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, g
import time


class MonitoringConfig:
    """Monitoring configuration"""
    
    # Log levels
    LOG_LEVEL = 'INFO'
    
    # Log file configuration
    LOG_DIR = '/app/logs'
    MAX_LOG_SIZE_MB = 100
    BACKUP_COUNT = 10
    
    # Metrics collection
    COLLECT_METRICS = True
    METRICS_INTERVAL_SECONDS = 60
    
    # Alert thresholds
    ERROR_RATE_THRESHOLD = 0.01  # 1%
    RESPONSE_TIME_THRESHOLD_MS = 2000
    CPU_THRESHOLD_PERCENT = 80
    MEMORY_THRESHOLD_PERCENT = 85
    DISK_THRESHOLD_PERCENT = 90


class StructuredLogger:
    """Structured JSON logging"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, MonitoringConfig.LOG_LEVEL))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(console_handler)
        
        # File handler (rotating)
        file_handler = logging.handlers.RotatingFileHandler(
            f"{MonitoringConfig.LOG_DIR}/app.log",
            maxBytes=MonitoringConfig.MAX_LOG_SIZE_MB * 1024 * 1024,
            backupCount=MonitoringConfig.BACKUP_COUNT
        )
        file_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(file_handler)
    
    def _get_formatter(self):
        """Get JSON formatter"""
        return JsonFormatter()
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)


class JsonFormatter(logging.Formatter):
    """Format logs as JSON"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                              'levelname', 'levelno', 'lineno', 'module', 'msecs',
                              'message', 'pathname', 'process', 'processName',
                              'relativeCreated', 'thread', 'threadName']:
                    log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class RequestLogger:
    """Log HTTP requests and responses"""
    
    @staticmethod
    def log_request():
        """Log incoming request"""
        g.start_time = time.time()
        
        logger = StructuredLogger('request')
        logger.info('Incoming request', 
                   method=request.method,
                   path=request.path,
                   remote_addr=request.remote_addr,
                   user_agent=request.headers.get('User-Agent'))
    
    @staticmethod
    def log_response(response):
        """Log outgoing response"""
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
            
            logger = StructuredLogger('response')
            logger.info('Outgoing response',
                       method=request.method,
                       path=request.path,
                       status_code=response.status_code,
                       duration_ms=round(duration_ms, 2))
            
            # Alert if slow response
            if duration_ms > MonitoringConfig.RESPONSE_TIME_THRESHOLD_MS:
                logger.warning('Slow response detected',
                             method=request.method,
                             path=request.path,
                             duration_ms=round(duration_ms, 2),
                             threshold_ms=MonitoringConfig.RESPONSE_TIME_THRESHOLD_MS)
        
        return response


class MetricsCollector:
    """Collect application metrics"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_error': 0,
            'response_times': [],
            'active_users': 0,
            'database_queries': 0
        }
    
    def record_request(self, success: bool, response_time_ms: float):
        """Record request metrics"""
        self.metrics['requests_total'] += 1
        if success:
            self.metrics['requests_success'] += 1
        else:
            self.metrics['requests_error'] += 1
        
        self.metrics['response_times'].append(response_time_ms)
        
        # Keep only last 1000 response times
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        response_times = self.metrics['response_times']
        
        return {
            'requests': {
                'total': self.metrics['requests_total'],
                'success': self.metrics['requests_success'],
                'error': self.metrics['requests_error'],
                'error_rate': self.metrics['requests_error'] / max(self.metrics['requests_total'], 1)
            },
            'response_time': {
                'avg_ms': sum(response_times) / len(response_times) if response_times else 0,
                'min_ms': min(response_times) if response_times else 0,
                'max_ms': max(response_times) if response_times else 0,
                'p95_ms': self._percentile(response_times, 95) if response_times else 0,
                'p99_ms': self._percentile(response_times, 99) if response_times else 0
            },
            'active_users': self.metrics['active_users'],
            'database_queries': self.metrics['database_queries']
        }
    
    @staticmethod
    def _percentile(data: list, percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class HealthCheck:
    """Application health check"""
    
    @staticmethod
    def check_database() -> bool:
        """Check database connectivity"""
        try:
            from database import db
            db.session.execute('SELECT 1')
            return True
        except Exception as e:
            logger = StructuredLogger('health')
            logger.error('Database health check failed', error=str(e))
            return False
    
    @staticmethod
    def check_redis() -> bool:
        """Check Redis connectivity"""
        try:
            import redis
            import os
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            r = redis.from_url(redis_url)
            r.ping()
            return True
        except Exception as e:
            logger = StructuredLogger('health')
            logger.error('Redis health check failed', error=str(e))
            return False
    
    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """Get overall health status"""
        db_healthy = HealthCheck.check_database()
        redis_healthy = HealthCheck.check_redis()
        
        overall_healthy = db_healthy and redis_healthy
        
        return {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'database': 'up' if db_healthy else 'down',
                'redis': 'up' if redis_healthy else 'down'
            }
        }


class AlertManager:
    """Manage alerts and notifications"""
    
    @staticmethod
    def send_alert(severity: str, title: str, message: str, **kwargs):
        """Send alert notification"""
        logger = StructuredLogger('alert')
        
        alert_data = {
            'severity': severity,
            'title': title,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        if severity == 'critical':
            logger.critical(f"ALERT: {title}", **alert_data)
        elif severity == 'warning':
            logger.warning(f"ALERT: {title}", **alert_data)
        else:
            logger.info(f"ALERT: {title}", **alert_data)
        
        # In production, send to Slack, PagerDuty, etc.
        # Example: send_slack_notification(alert_data)
        # Example: send_pagerduty_alert(alert_data)
    
    @staticmethod
    def check_thresholds(metrics: Dict[str, Any]):
        """Check metrics against thresholds and send alerts"""
        # Check error rate
        error_rate = metrics['requests']['error_rate']
        if error_rate > MonitoringConfig.ERROR_RATE_THRESHOLD:
            AlertManager.send_alert(
                'warning',
                'High Error Rate',
                f'Error rate is {error_rate:.2%}, threshold is {MonitoringConfig.ERROR_RATE_THRESHOLD:.2%}',
                error_rate=error_rate
            )
        
        # Check response time
        avg_response_time = metrics['response_time']['avg_ms']
        if avg_response_time > MonitoringConfig.RESPONSE_TIME_THRESHOLD_MS:
            AlertManager.send_alert(
                'warning',
                'Slow Response Time',
                f'Average response time is {avg_response_time:.0f}ms, threshold is {MonitoringConfig.RESPONSE_TIME_THRESHOLD_MS}ms',
                avg_response_time_ms=avg_response_time
            )


def configure_monitoring(app: Flask):
    """Configure monitoring middleware"""
    
    # Request logging
    @app.before_request
    def before_request():
        RequestLogger.log_request()
    
    @app.after_request
    def after_request(response):
        return RequestLogger.log_response(response)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return HealthCheck.get_health_status()
    
    # Metrics endpoint
    metrics_collector = MetricsCollector()
    
    @app.route('/api/metrics')
    def metrics():
        return metrics_collector.get_metrics()
    
    print("✓ Monitoring configuration applied")


# Global logger instance
logger = StructuredLogger('alphalearning')


if __name__ == '__main__':
    # Test logging
    logger.info('Application started', version='1.0.0')
    logger.warning('This is a warning', user_id=123)
    logger.error('This is an error', error_code='E001')
    
    # Test health check
    health = HealthCheck.get_health_status()
    print(json.dumps(health, indent=2))

