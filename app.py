# app.py
from flask import Flask, g, session
from db import db, init_db
import os

print("DATABASE_URL:", os.getenv("DATABASE_URL"))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Load DATABASE_URL
db_uri = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
init_db(app)

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