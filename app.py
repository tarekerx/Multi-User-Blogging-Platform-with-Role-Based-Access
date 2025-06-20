# app.py
from flask import Flask, g, session
from db import db, migrate  # Make sure this imports both
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate.init_app(app)

# Import models inside app context
@app.cli.command("init-db")
def init_db():
    """Create all tables."""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tables created in app context")
        except Exception as e:
            print("❌ Error creating tables:", str(e))

# Import models and blueprints after db setup
with app.app_context():
    try:
        from models import Post, Author, Comment
    except Exception as e:
        print("❌ Error importing models:", str(e))

    # Optional: Create tables here too
    try:
        db.create_all()
        print("✅ Tables created at startup")
    except Exception as e:
        print("❌ Error creating tables at startup:", str(e))

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