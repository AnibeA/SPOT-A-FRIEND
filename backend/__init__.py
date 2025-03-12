from flask import Flask  # Flask framework to create the application
from backend.config import Config  # Configuration settings (database, secret keys, etc.)
from backend.extensions import db, migrate, bcrypt, cors  # Extensions for database, migrations, security, and CORS
from backend.auth_routes import auth  # Import authentication-related routes
from backend.routes import main  # ✅ Import general routes (home page, etc.)
from backend.user_comparison import comparison  # ✅ Import user comparison routes

def create_app():
    """
    Application factory function: 
    - Creates and configures the Flask app instance
    - Initializes extensions (DB, migrations, security, CORS)
    - Registers Blueprints (modular routes)
    """
    
    # ✅ Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)  # ✅ Load configuration settings

    # ✅ Initialize Flask extensions
    db.init_app(app)  # Initialize the database (SQLAlchemy)
    migrate.init_app(app, db)  # Enable database migrations (Flask-Migrate)
    bcrypt.init_app(app)  # Initialize Bcrypt for password hashing
    cors.init_app(app)  # Enable Cross-Origin Resource Sharing (CORS)

    # ✅ Register Blueprints (modular route handlers)
    app.register_blueprint(auth)  # Authentication routes (e.g., /login, /callback, /logout)
    app.register_blueprint(main)  # General routes (e.g., home page /)
    app.register_blueprint(comparison)  # ✅ Register the user comparison routes

    return app  # ✅ Return the Flask app instance
