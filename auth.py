from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash


auth_bp = Blueprint('auth', __name__, template_folder='templates')
from db import get_db


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form.get('name')
        password = generate_password_hash(request.form.get('password'))
        email = request.form.get('email')
        emails = get_db().execute('SELECT email FROM authors').fetchall()

        if not name or not password:
            flash('Name and password are required!', 'error')
            return redirect(url_for('auth.register'))
        

        if email in [email['email'] for email in emails]:
            flash('Email already exists!', 'error')
            return redirect(url_for('auth.register'))


        db = get_db()
        db.execute('INSERT INTO authors (name, password, email) VALUES (?, ?, ?)', (name, password, email))
        db.commit()
        return redirect(url_for('auth.login'))

    return render_template('users/register.html', page_title="Register User")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = get_db()
        user = db.execute('SELECT * FROM authors WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['id'] = user['id']
            session['user_name'] = user['name']
            session['email'] = user['email']
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
        emails = get_db().execute('SELECT email FROM authors').fetchall()


        
        if email in [email['email'] for email in emails] and email != g.email:
            flash('Email already exists!', 'error')
            return redirect(url_for('auth.register'))
        
        if not name or not email:
            flash('Name and email are required!', 'error')
            return redirect(url_for('auth.profile'))

        if password:
            password = generate_password_hash(password)
        else:
            password = g.get('password', None)
        
        db = get_db()
        db.execute('UPDATE authors SET name = ?, email = ?, password = ? WHERE id = ?', (name, email,password, g.user_id))
        db.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))


    if g.user_id is None:
        flash('You need to be logged in to view your profile.', 'error')
        redirect(url_for('auth.login'))

    db = get_db()
    user = db.execute('SELECT * FROM authors WHERE id = ?', (g.user_id,)).fetchone()

    return render_template('users/user_profile.html', page_title="Profile", user=user)