from backend import create_app  # Import the create_app function to initialize the Flask app
from backend.extensions import db, migrate  # Import database (SQLAlchemy) and migration tools (Flask-Migrate)
from backend.models import User  # Import the User model (ensures it's recognized when initializing DB)

# ✅ Create the Flask application instance
app = create_app()

# ✅ Ensure database tables are created before running the app
# The `app.app_context()` ensures database operations are performed in the correct application context.
with app.app_context():
    db.create_all()  # Creates all tables defined in models.py (if they don't exist already)

# ✅ Run the application
if __name__ == "__main__":
    app.run(debug=True)  # Starts the Flask app in debug mode for development purposes
