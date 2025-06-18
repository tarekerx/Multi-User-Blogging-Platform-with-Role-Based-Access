# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from models import Author
from sqlalchemy.exc import IntegrityError
from db   import db
auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        password = generate_password_hash(request.form.get('password'))
        email = request.form.get('email')

        if not name or not password:
            flash('Name and password are required!', 'error')
            return redirect(url_for('auth.register'))

        try:
            new_user = Author(name=name, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))

        except IntegrityError:
            db.session.rollback()
            flash('Email already exists!', 'error')
            return redirect(url_for('auth.register'))

    return render_template('users/register.html', page_title="Register User")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Author.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['id'] = user.id
            session['user_name'] = user.name
            session['email'] = user.email
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('blog.posts'))

        flash('Invalid credentials.', 'error')

    return render_template('users/login.html', page_title="Login")


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('blog.posts'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email:
            flash('Name and email are required!', 'error')
            return redirect(url_for('auth.profile'))

        user = Author.query.get(g.user_id)
        user.name = name
        user.email = email

        if password:
            user.password = generate_password_hash(password)

        db.session.commit()
        session['user_name'] = user.name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    if g.user_id is None:
        flash('You need to be logged in to view your profile.', 'error')
        return redirect(url_for('auth.login'))

    user = Author.query.get(g.user_id)
    return render_template('users/user_profile.html', page_title="Profile", user=user)


@auth_bp.route('/delete', methods=["GET", "POST"])
def delete_user():
    if g.user_id is None:
        flash('You need to be logged in to delete your account.', 'error')
        return redirect(url_for('auth.login'))

    user = Author.query.get(g.user_id)
    db.session.delete(user)
    db.session.commit()

    session.clear()
    flash('Your account has been deleted successfully.', 'success')
    return redirect(url_for('blog.posts'))


@auth_bp.route('/be_admin', methods=['GET', 'POST'])
def be_admin():
    if g.user_id is None:
        flash('You need to be logged in to be an admin.', 'error')
        return redirect(url_for('auth.login'))

    if g.is_admin == 1:
        flash('You are already an admin!', 'error')
        return redirect(url_for('blog.posts'))

    if request.method == 'POST':
        user = Author.query.get(g.user_id)
        user.is_admin = 1
        db.session.commit()
        session['is_admin'] = 1
        flash('You are now an admin!', 'success')
        return redirect(url_for('blog.posts'))

    return render_template('users/be_admin.html', page_title="Become Admin")