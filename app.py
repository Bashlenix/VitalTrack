"""
Main Flask application factory for the EHR system.
"""

from flask import Flask
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


def create_app():
    """Application factory pattern for creating Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure secret key is configured for sessions
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = secrets.token_hex(32)
        print(
            "Warning: Using auto-generated secret key. Set SECRET_KEY in .env for production."
        )

    # Initialize extensions
    db.init_app(app)
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


# Create the application instance
app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
