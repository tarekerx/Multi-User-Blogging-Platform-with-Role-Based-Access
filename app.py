# app.py
from flask import Flask, g, session
from db import db  # Import both db and migrate
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback_secret_key")
db_uri = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize DB and Migrate with the app

@app.cli.command("init-db")
def init_db():
    """Create all tables."""
    with app.app_context():
        from models import Post, Author, Comment
        db.create_all()
    print("✅ Tables created.")
# Import models after initializing db
with app.app_context():
    from models import Post, Author, Comment  # Or just import models


# Register Blueprints
from auth import auth_bp
from blog import blog_bp
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(blog_bp, url_prefix="/")

@app.route('/db-test')
def db_test():
    try:
        from models import Post
        Post.query.first()
        return "✅ Connected to PostgreSQL, and table exists."
    except Exception as e:
        return f"❌ Error: {str(e)}"
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