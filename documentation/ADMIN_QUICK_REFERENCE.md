# 🔧 Flask Security Portal - Admin Quick Reference Guide

## 🚀 Quick Start Commands

### Start the Application
```bash
cd /path/to/tanger-alliance-sensibilisation-portal
source venv/bin/activate
python app.py
```

### Access Points
- **Main Application:** http://127.0.0.1:5002
- **Admin Interface:** http://127.0.0.1:5002/admin/
- **Login Page:** http://127.0.0.1:5002/auth/login

### Admin Credentials
```
Email: set TANGER_ADMIN_EMAIL before seeding
Password: set TANGER_ADMIN_PASSWORD before seeding
Role: admin
```

## 📊 Admin Interface Sections

### 1. User Management (`/admin/user/`)
- **View all users** - List, search, and filter users
- **Add new users** - Create accounts with temporary passwords
- **Edit user details** - Update profiles, roles, departments
- **Activate/Deactivate** - Control user access with `is_active` field
- **Password management** - Reset user passwords

### 2. Module Management (`/admin/module/`)
- **Training modules** - Manage security training content
- **Module structure** - Organize learning paths
- **Content updates** - Edit module descriptions and materials
- **Progress tracking** - Monitor user completion rates

### 3. Campaign Management (`/admin/campaign/`)
- **Phishing campaigns** - Create and manage phishing simulations
- **Target management** - Select campaign participants
- **Results analysis** - View campaign effectiveness
- **Reporting** - Generate campaign reports

### 4. System Configuration (`/admin/systemconfig/`)
- **System settings** - Configure application parameters
- **Security options** - Adjust security policies
- **Email configuration** - Setup notification systems
- **Backup settings** - Configure automatic backups
- **Integration settings** - Manage third-party integrations

## 🛠️ Daily Administration Tasks

### Morning Checklist
1. **Check Application Status**
   ```bash
   curl -I http://127.0.0.1:5002
   ```

2. **Verify Database Connectivity**
   ```bash
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('DB OK' if db.engine.execute('SELECT 1').scalar() == 1 else 'DB ERROR')"
   ```

3. **Check Recent User Activity**
   - Access `/admin/user/` and review recent logins
   - Monitor user registration requests

### Weekly Maintenance
1. **Database Backup**
   ```bash
   cp instance/tanger_alliance.db backups/tanger_alliance_$(date +%Y%m%d).bak
   ```

2. **Review Security Logs**
   - Check authentication failures
   - Review admin actions
   - Monitor suspicious activity

3. **Update User Training Status**
   - Check completion rates
   - Send reminders to inactive users
   - Update training materials if needed

## 🔒 Security Management

### User Account Management
```python
# Add new admin user (Python console)
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User(
        email='new.admin@tangeralliance.com',
        firstname='Admin',
        lastname='User',
        password=generate_password_hash('secure_password'),
        role='admin',
        is_active=True
    )
    db.session.add(admin)
    db.session.commit()
```

### Reset User Password
1. Access `/admin/user/`
2. Find the user account
3. Click "Edit"
4. Enter new password in password field
5. Save changes
6. Temporary password will be displayed

### Deactivate Compromised Account
1. Access `/admin/user/`
2. Find the user account
3. Edit the user
4. Uncheck "Is Active"
5. Save changes

## 🧪 Testing & Troubleshooting

### Test Admin Access
```bash
python test_admin.py
```

### Check Database Schema
```python
from app import create_app, db
app = create_app()
with app.app_context():
    print(db.metadata.tables.keys())
```

### Verify CSRF Protection
- CSRF tokens should be present in all forms
- Login attempts without CSRF token should fail
- Error template should render properly

### Common Issues & Solutions

#### 1. "Template Not Found" Error
```bash
# Check template exists
ls -la app/templates/errors/400_csrf.html
ls -la app/templates/admin/system_config.html
```

#### 2. Database Connection Issues
```bash
# Recreate database if corrupted
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"
```

#### 3. Import Errors
```bash
# Verify Flask-Admin installation
pip list | grep Flask-Admin
# Reinstall if needed
pip install Flask-Admin
```

## 📈 Monitoring & Analytics

### User Statistics Dashboard
- Total active users
- Training completion rates
- Recent login activity
- Security incident reports

### Performance Metrics
- Page load times
- Database query performance
- User session duration
- Error rates

### Security Metrics
- Failed login attempts
- Admin action audit log
- Password change frequency
- Security training compliance

## 🔄 Regular Updates

### Application Updates
1. Backup database before updates
2. Test in development environment
3. Deploy during maintenance window
4. Verify all functionality post-update

### Security Updates
- Regular password policy reviews
- Update training materials quarterly
- Review admin access permissions monthly
- Security vulnerability assessments

## 📞 Emergency Procedures

### Application Down
1. Check process status: `ps aux | grep python`
2. Check logs: `tail -f /var/log/portail-securite.log`
3. Restart application: `sudo systemctl restart portail-securite`

### Security Incident
1. **Immediate:** Deactivate compromised accounts
2. **Document:** Log incident details
3. **Investigate:** Review access logs
4. **Report:** Notify security team
5. **Remediate:** Implement fixes
6. **Follow-up:** Monitor for recurrence

### Database Corruption
1. Stop application
2. Restore from latest backup
3. Verify data integrity
4. Restart application
5. Test functionality

## 📚 Documentation References

- **Technical Documentation:** `/docs/`
- **API Documentation:** Flask-Admin official docs
- **Security Policies:** Company security handbook
- **Training Materials:** `/app/templates/modules/`

## 📝 Change Log Template

```
Date: YYYY-MM-DD
Administrator: [Name]
Changes Made:
- [Description of changes]
- [Users affected]
- [Systems modified]

Testing Performed:
- [Test results]
- [Verification steps]

Notes:
- [Additional observations]
- [Follow-up required]
```

---

**Last Updated:** June 7, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
