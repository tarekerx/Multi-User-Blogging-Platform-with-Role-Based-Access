# app.py
from flask import Flask, g, session
from db import db, migrate  # Import both db and migrate
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback_secret_key")

# Load DATABASE_URL
db_uri = os.getenv("DATABASE_URL")
if not db_uri:
    raise ValueError("DATABASE_URL environment variable not set!")

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB and Migrate
migrate.init_app(app)

# Import models before CLI commands or any queries
from models import Post, Author, Comment  # Make sure these are defined in models.py

@app.cli.command("init-db")
def init_db():
    """Create all database tables."""
    db.create_all()
    print("✅ Tables created.")

# Register Blueprints
from auth import auth_bp
from blog import blog_bp
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(blog_bp, url_prefix="/")

@app.before_request
def load_logged_in_user():
    user_id = session.get('id')
    if user_id:
        g.user_id = user_id
        g.user_name = session.get('user_name')
        g.email = session.get('email')
        g.is_admin = session.get('is_admin')
    else:
        g.user_id = None


if __name__ == '__main__':
    app.run(debug=True)