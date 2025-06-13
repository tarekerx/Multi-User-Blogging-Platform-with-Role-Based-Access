from flask import Flask, g, session
import sqlite3
from auth import auth_bp
from blog import blog_bp
from db import get_db


app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey123"


# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(blog_bp,url_prefix="/")

# Database Connection


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.before_request
def load_logged_in_user():
    user_id = session.get('id')
    if user_id:
        g.user_id = user_id
        g.user_name = session.get('user_name')
        g.email = session.get('email')
    else:
        g.user_id = None

if __name__ == '__main__':
    app.run(debug=True)
