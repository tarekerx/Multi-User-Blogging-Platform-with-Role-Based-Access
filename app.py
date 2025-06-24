# app.py
from flask import Flask, g, session
from db import db, migrate
import os
from auth import init_oauth
from alembic import command
from alembic.config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init extensions
db.init_app(app)
migrate.init_app(app, db)
init_oauth(app)

def run_auto_migration():
    migrations_path = os.path.join(os.path.dirname(__file__), 'migrations')
    alembic_ini_path = os.path.join(migrations_path, 'alembic.ini')

    if not os.path.exists(migrations_path) or not os.path.exists(alembic_ini_path):
        print("❌ Alembic not initialized. Run this once:")
        print("   flask db init && flask db migrate -m 'init' && flask db upgrade")
        return

    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option('script_location', migrations_path)

    try:
        command.revision(alembic_cfg, autogenerate=True, message="Auto migration")
        print("⚠️ Auto migration script created")
    except Exception as e:
        if "Target database is not up to date" not in str(e):
            print("⚠️ Revision issue:", str(e))

    try:
        command.upgrade(alembic_cfg, 'head')
        print("✅ Auto upgrade done")
    except Exception as e:
        print("❌ Upgrade failed:", str(e))


@app.cli.command("init-db")
def init_db():
    """Manual: Create all tables."""
    with app.app_context():
        try:
            run_auto_migration()
            db.create_all()
            print("✅ Tables created manually")
        except Exception as e:
            print("❌ Error creating tables:", str(e))


# Models and auto-migration
with app.app_context():
    try:
        from models import Post, Author, Comment  # Load models
        run_auto_migration()
    except Exception as e:
        print("❌ Error during model import or migration:", str(e))

# Blueprints
from auth import auth_bp
from blog import blog_bp
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(blog_bp, url_prefix="/")


# DB Test route
@app.route('/db-test')
def db_test():
    try:
        from models import Post
        Post.query.first()
        return "✅ Connected to DB, and table exists."
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Load user info before each request
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
