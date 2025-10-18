# Alpha Learning Platform - Deployment Guide

## Table of Contents

1. [Production Setup](#production-setup)
2. [Security Configuration](#security-configuration)
3. [Monitoring & Logging](#monitoring--logging)
4. [Deployment Process](#deployment-process)
5. [Post-Deployment](#post-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Production Setup

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL 15+ database
- Redis 7+ cache
- SSL certificates
- Domain name configured
- Cloud storage (AWS S3 or equivalent)
- Email service (SendGrid or AWS SES)

### Environment Variables

Create `.env.production` file with the following variables:

```bash
# Database
DB_NAME=alphalearning
DB_USER=alphalearning
DB_PASSWORD=<strong-password>
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}

# Redis
REDIS_PASSWORD=<strong-password>
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# Application
FLASK_ENV=production
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
JWT_SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>

# Email
SENDGRID_API_KEY=<your-sendgrid-api-key>
FROM_EMAIL=noreply@alphalearning.com

# File Storage
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_S3_BUCKET=alphalearning-uploads
AWS_REGION=us-east-1

# Monitoring
SENTRY_DSN=<your-sentry-dsn>

# Security
ALLOWED_HOSTS=alphalearning.com,www.alphalearning.com
CORS_ORIGINS=https://alphalearning.com,https://www.alphalearning.com
```

### Build and Deploy

```bash
# Build production image
docker-compose -f docker-compose.production.yml build

# Start services
docker-compose -f docker-compose.production.yml up -d

# Run database migrations
docker-compose -f docker-compose.production.yml exec app flask db upgrade

# Create initial admin user
docker-compose -f docker-compose.production.yml exec app python create_admin.py
```

### SSL/TLS Configuration

1. Obtain SSL certificates (Let's Encrypt recommended)
2. Place certificates in `./ssl` directory
3. Update nginx configuration with certificate paths
4. Restart nginx service

---

## Security Configuration

### Password Policy

The platform enforces strong password requirements:
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Account Lockout

- Maximum 5 failed login attempts
- 30-minute lockout duration
- Automatic unlock after duration expires

### Rate Limiting

- 60 requests per minute per IP
- 1000 requests per hour per IP
- Custom limits for sensitive endpoints

### Security Headers

All responses include security headers:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000
- Content-Security-Policy: (configured)
- Referrer-Policy: strict-origin-when-cross-origin

### File Upload Security

- Maximum file size: 10MB
- Allowed extensions: jpg, jpeg, png, gif, pdf, doc, docx
- Filename sanitization
- Virus scanning (recommended in production)

### Data Encryption

- All data encrypted in transit (HTTPS)
- Sensitive data encrypted at rest
- Database encryption enabled
- Secure password hashing (PBKDF2-SHA256)

---

## Monitoring & Logging

### Application Monitoring

**Metrics Collected:**
- Request count (total, success, error)
- Response times (avg, min, max, p95, p99)
- Active users
- Database query count
- Error rates

**Health Checks:**
- Database connectivity
- Redis connectivity
- External service availability
- System resource usage

### Logging

**Log Levels:**
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical issues

**Log Format:**
Structured JSON logging with fields:
- timestamp
- level
- logger
- message
- module, function, line
- custom fields (user_id, request_id, etc.)

**Log Files:**
- Location: `/app/logs/`
- Rotation: 100MB per file
- Retention: 10 backup files

### Alerting

**Alert Thresholds:**
- Error rate > 1%
- Response time > 2000ms
- CPU usage > 80%
- Memory usage > 85%
- Disk usage > 90%

**Alert Channels:**
- Email notifications
- Slack integration
- PagerDuty (for critical alerts)

### Monitoring Endpoints

```bash
# Health check
GET /api/health

# Metrics
GET /api/metrics

# System status
GET /api/admin/system-status
```

---

## Deployment Process

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance testing completed
- [ ] Database backup created
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Team notified

### Deployment Steps

1. **Backup Current System**
   ```bash
   # Backup database
   docker-compose exec db pg_dump -U alphalearning alphalearning > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # Backup uploads
   docker-compose exec app tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz /app/uploads
   ```

2. **Pull Latest Code**
   ```bash
   git pull origin main
   ```

3. **Build New Images**
   ```bash
   docker-compose -f docker-compose.production.yml build
   ```

4. **Run Database Migrations**
   ```bash
   docker-compose -f docker-compose.production.yml run app flask db upgrade
   ```

5. **Deploy New Version**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

6. **Verify Deployment**
   ```bash
   # Check health
   curl https://alphalearning.com/api/health
   
   # Check logs
   docker-compose -f docker-compose.production.yml logs -f app
   ```

### Rollback Procedure

If deployment fails:

1. **Stop New Version**
   ```bash
   docker-compose -f docker-compose.production.yml down
   ```

2. **Restore Database**
   ```bash
   docker-compose exec db psql -U alphalearning alphalearning < backup_TIMESTAMP.sql
   ```

3. **Deploy Previous Version**
   ```bash
   git checkout <previous-commit>
   docker-compose -f docker-compose.production.yml up -d
   ```

---

## Post-Deployment

### Verification Steps

1. **Smoke Tests**
   - [ ] Homepage loads
   - [ ] User login works
   - [ ] Student dashboard accessible
   - [ ] Teacher dashboard accessible
   - [ ] Admin dashboard accessible
   - [ ] API endpoints responding

2. **Performance Check**
   - [ ] Response times < 2s
   - [ ] No error spikes
   - [ ] Database queries optimized
   - [ ] Cache hit rate acceptable

3. **Security Verification**
   - [ ] HTTPS working
   - [ ] Security headers present
   - [ ] Authentication working
   - [ ] Rate limiting active

### Monitoring First 24 Hours

- Monitor error rates closely
- Watch response times
- Check resource usage (CPU, memory, disk)
- Review user feedback
- Track key business metrics

### User Communication

- Send deployment announcement
- Update status page
- Notify support team
- Prepare for user questions

---

## Troubleshooting

### Common Issues

**Issue: Application won't start**
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs app

# Check environment variables
docker-compose -f docker-compose.production.yml config

# Verify database connection
docker-compose -f docker-compose.production.yml exec app python -c "from database import db; db.session.execute('SELECT 1')"
```

**Issue: Database connection failed**
```bash
# Check database status
docker-compose -f docker-compose.production.yml ps db

# Check database logs
docker-compose -f docker-compose.production.yml logs db

# Test connection
docker-compose -f docker-compose.production.yml exec db psql -U alphalearning -d alphalearning -c "SELECT 1"
```

**Issue: Slow performance**
```bash
# Check resource usage
docker stats

# Check slow queries
docker-compose -f docker-compose.production.yml exec db psql -U alphalearning -d alphalearning -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10"

# Check cache hit rate
docker-compose -f docker-compose.production.yml exec redis redis-cli INFO stats
```

**Issue: High error rate**
```bash
# Check application logs
docker-compose -f docker-compose.production.yml logs app | grep ERROR

# Check metrics
curl https://alphalearning.com/api/metrics

# Review recent deployments
git log -10 --oneline
```

### Emergency Contacts

- **Technical Lead:** [contact info]
- **DevOps Team:** [contact info]
- **On-Call Engineer:** [contact info]
- **Emergency Hotline:** [phone number]

### Support Resources

- **Documentation:** https://docs.alphalearning.com
- **Status Page:** https://status.alphalearning.com
- **Issue Tracker:** https://github.com/alphalearning/platform/issues
- **Slack Channel:** #platform-support

---

## Security Incident Response

### If Security Breach Detected:

1. **Immediate Actions**
   - Isolate affected systems
   - Preserve evidence (logs, snapshots)
   - Notify security team
   - Activate incident response plan

2. **Assessment**
   - Determine scope of breach
   - Identify affected data
   - Assess impact on users
   - Document timeline

3. **Containment**
   - Block malicious access
   - Patch vulnerabilities
   - Reset compromised credentials
   - Update security rules

4. **Communication**
   - Notify affected users
   - Report to authorities (if required)
   - Update status page
   - Prepare public statement

5. **Recovery**
   - Restore from clean backups
   - Verify system integrity
   - Monitor for re-infection
   - Implement additional security

6. **Post-Incident**
   - Conduct post-mortem
   - Update security procedures
   - Improve monitoring
   - Train team on lessons learned

---

## Compliance

### GDPR Compliance

- Data processing agreements in place
- User consent mechanisms implemented
- Data export functionality available
- Data deletion procedures established
- Privacy policy published

### COPPA Compliance

- Parental consent for users under 13
- Limited data collection for children
- No behavioral advertising to children
- Secure data storage
- Compliance documentation maintained

### SOC 2 Compliance (if applicable)

- Security controls documented
- Access controls implemented
- Audit logging enabled
- Regular security assessments
- Third-party audits conducted

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error rates
- Check system health
- Review critical alerts
- Verify backups

**Weekly:**
- Review performance metrics
- Check security logs
- Update dependencies
- Test backup restoration

**Monthly:**
- Security vulnerability scan
- Performance optimization review
- Capacity planning review
- Documentation updates

**Quarterly:**
- Disaster recovery drill
- Security audit
- Penetration testing
- Compliance review

---

## Contact Information

**Development Team:**
- Email: dev@alphalearning.com
- Slack: #dev-team

**Operations Team:**
- Email: ops@alphalearning.com
- Slack: #ops-team

**Security Team:**
- Email: security@alphalearning.com
- Slack: #security-team

**Support Team:**
- Email: support@alphalearning.com
- Slack: #support-team

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Next Review:** January 2026

