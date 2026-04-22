# Tanger Alliance Security Awareness Portal

Web training platform for employee cybersecurity awareness. The portal combines learning modules, quizzes, phishing simulations, progress tracking, and an admin surface for running awareness campaigns inside an organization.

## Highlights

- Flask application with modular blueprints for auth, learning content, security resources, and admin flows
- SQLAlchemy-backed progress tracking, badges, certificates, and quiz scoring
- Phishing-simulation pages and awareness-content workflows aimed at internal training
- Admin tooling for user management, module management, and operational reporting
- Full pytest suite covering auth, dashboard, quiz, security, admin, and integration paths

## Stack

- Python 3
- Flask, Flask-Login, Flask-WTF, Flask-Admin
- SQLAlchemy / Flask-SQLAlchemy
- SQLite for local development, PostgreSQL-ready production configuration
- Bootstrap-based server-rendered frontend

## Repository layout

```text
app/
├── models/
├── routes/
├── templates/
├── static/
└── utils/
tests/
migrations/
docs/
scripts/
app.py
config.py
requirements.txt
```

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask db upgrade
python app.py
```

The development server starts on `http://127.0.0.1:5002`.

## Environment configuration

The repository ships with `.env.example`. For local use, create `.env` and set values such as:

- `SECRET_KEY`
- `DEV_DATABASE_URL`
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`
- `TANGER_ADMIN_EMAIL`
- `TANGER_ADMIN_PASSWORD`

## Testing

Run the full validation suite with:

```bash
pytest -q
```

The public version of this repository was revalidated with the full suite passing locally.

## Notes

- Local development defaults to SQLite.
- Production configuration expects environment-driven secrets and a PostgreSQL connection string.
- Repository secrets are not stored in git; use local environment files or deployment secrets instead.

## License

Proprietary - Tanger Alliance Security Team
