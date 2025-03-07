from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS

db = SQLAlchemy()  # ✅ Ensure only one instance of SQLAlchemy is created
migrate = Migrate()
bcrypt = Bcrypt()
cors = CORS()
