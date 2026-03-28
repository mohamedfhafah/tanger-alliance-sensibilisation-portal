# Tanger Alliance Security Awareness Portal

## 🎉 Project Status: PRODUCTION READY ✅

**Phase 4 Completed**: June 8, 2025  
**Production Deployment**: Ready for live deployment  
**All Critical Issues**: Resolved ✅  

## Project Overview

The Tanger Alliance Security Awareness Portal is a web-based platform designed to enhance the cybersecurity awareness and knowledge of employees through structured learning modules, interactive quizzes, and simulated phishing campaigns. The application helps organizations manage and track employee progress in security training, identify vulnerable areas, and demonstrate compliance with security awareness requirements.

## Technology Stack

- **Backend**: Python 3 with Flask framework
- **Database**: SQLAlchemy ORM (configurable for SQLite in development, PostgreSQL in production)
- **Authentication**: Flask-Login, Flask-Bcrypt for password hashing
- **Forms**: Flask-WTF with CSRF protection
- **Admin Interface**: Flask-Admin
- **Email Services**: Flask-Mail
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 4
- **Environment Management**: Python virtual environment with configuration via .env files

## Project Structure

```
Projet_Portail_Securite/
├── app/                          # Main application package
│   ├── __init__.py               # Application factory pattern implementation
│   ├── forms.py                  # Form definitions
│   ├── models/                   # Database models
│   │   ├── user.py               # User authentication and profile models
│   │   ├── module.py             # Learning modules and quiz models
│   │   ├── campaign.py           # Phishing campaign models
│   │   └── settings.py           # Application settings model
│   ├── routes/                   # Application routes
│   │   ├── main.py               # Main routes (home, dashboard)
│   │   ├── auth.py               # Authentication routes (login, register, password reset)
│   │   ├── modules.py            # Training module routes
│   │   └── admin/                # Administration routes
│   ├── static/                   # Static assets (CSS, JS, images)
│   ├── templates/                # Jinja2 HTML templates
│   ├── utils/                    # Utility functions
│   └── seed_data.py              # Initial data seeding
├── migrations/                   # Database migrations
├── tests/                        # Test suite
├── logs/                         # Application logs
├── docs/                         # Documentation
├── scripts/                      # Maintenance and utility scripts
├── app.py                        # Application entry point
├── config.py                     # Configuration settings
├── requirements.txt              # Project dependencies
└── .env                          # Environment variables (not tracked in git)
```

## Core Features

### 1. User Management

- User registration and authentication
- Role-based access control (admin/user)
- Password reset functionality via email
- User profile management
- Department-based organization

### 2. Security Awareness Training

- Structured learning modules with content and images
- Interactive quizzes with various question types
- Progress tracking for users
- Completion certificates
- Learning path customization

### 3. Phishing Simulation Campaigns

- Campaign creation and management
- Phishing email template selection
- Target user selection
- Tracking of opened, clicked, and reported emails
- Performance analytics and reporting

### 4. Administration

- User management interface
- Content management for training modules
- Quiz creation and editing
- Campaign scheduling and monitoring
- System settings configuration
- Analytics dashboard

### 5. Database Management

- Automatic database creation and migration
- Data backup and restoration utilities
- Scheduled backups with configurable retention

## 🚀 Quick Start

### Ready-to-Use Application
The application is fully configured and ready to run:

```bash
# 1. Navigate to project directory
cd /Users/mohamedfhafah/Documents/Analyse_Cecurité/Projet_Portail_Securite

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start application
python app.py

# 4. Access in browser
open http://127.0.0.1:5013
```

### Admin Access
- **Email**: admin@tangeralliance.com
- **Password**: set `TANGER_ADMIN_PASSWORD` before running the seed script
- **Dashboard**: Full admin controls and analytics

### Database Status
- **Users**: 1 admin user configured
- **Modules**: 6 security training modules
- **Quizzes**: 20 interactive assessments
- **Status**: All data verified and ready

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (optional but recommended)
- SMTP server for email functionality

### Installation Steps

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Configure environment variables in `.env` file
5. Initialize the database: `flask db upgrade`
6. Seed initial data (optional): `flask seed-data`
7. Run the application: `python app.py`

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
FLASK_APP=app.py
FLASK_ENV=development  # Change to production for deployment
SECRET_KEY=your_secret_key_here
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_DEFAULT_SENDER=noreply@example.com
```

## Development and Testing

### Running Tests

```
python -m pytest
```

### Development Server

```
python app.py
```

The application will be available at http://localhost:5002

## Deployment

The application supports multiple deployment configurations:

- **Development**: Local SQLite database
- **Testing**: In-memory SQLite database
- **Production**: PostgreSQL database with enhanced security
- **Docker**: Containerized deployment with optimized logging

## License

Proprietary - Tanger Alliance Security Team
