"""
Main Flask application factory for the EHR system.
"""

import os
from flask import Flask, request
from flask_wtf.csrf import CSRFError, CSRFProtect
from config import Config
from models import db
from utils.mail_helper import init_mail

# Import all blueprints
from routes.auth import auth_bp
import secrets
from routes.main import main_bp
from routes.patients import patients_bp
from routes.appointments import appointments_bp
from routes.lab_results import lab_results_bp
from routes.radiology import radiology_bp
from routes.doctor import doctor_bp
from routes.medical_history import medical_history_bp


def create_app(config_overrides=None):
    """Application factory pattern for creating Flask app.
    config_overrides (dict) is applied on top of Config, e.g. by tests."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    # The secret key signs session cookies and CSRF tokens. A random key per
    # process would break logins across gunicorn workers, so only tests may
    # run without one.
    if not app.config.get("SECRET_KEY"):
        if not app.config.get("TESTING"):
            raise RuntimeError(
                "SECRET_KEY is not set. Generate one with scripts/generate_secrets.py "
                "and put it in .env."
            )
        app.config["SECRET_KEY"] = secrets.token_hex(32)

    # Initialize extensions
    db.init_app(app)
    # Every POST must carry the session's CSRF token (rejected with 400 otherwise)
    CSRFProtect(app)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        app.logger.warning("CSRF check failed on %s: %s", request.path, error.description)
        message = (
            "Your session expired or the form was invalid. "
            "Please go back, reload the page and submit again."
        )
        return message, 400
    init_mail(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(lab_results_bp)
    app.register_blueprint(radiology_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(medical_history_bp)

    return app


def dev_server_options():
    """Options for the local development server (python app.py).
    Debug mode exposes the Werkzeug debugger, so it is off unless FLASK_DEBUG=1.
    The Docker image runs gunicorn instead and never uses these options."""
    return {
        "host": os.getenv("FLASK_HOST", "127.0.0.1"),
        "port": int(os.getenv("FLASK_PORT", 5000)),
        "debug": os.getenv("FLASK_DEBUG", "0") == "1",
    }


# Create the application instance
app = create_app()


if __name__ == "__main__":
    options = dev_server_options()
    print(f" * Flask app running at http://{options['host']}:{options['port']}")
    app.run(**options)
