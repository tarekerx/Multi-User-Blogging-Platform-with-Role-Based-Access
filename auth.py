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

        cur = get_db().cursor()
        cur.execute('SELECT email FROM authors')
        emails = cur.fetchall()

        cur.execute('SELECT name FROM authors')
        names = cur.fetchall()


        if not name or not password:
            flash('Name and password are required!', 'error')
            return redirect(url_for('auth.register'))

        if any(e['email'] == email for e in emails):
            flash('Email already exists!', 'error')
            return redirect(url_for('auth.register'))

        if any(e['name'] ==name for e in names):
            flash('User name already exists!', 'error')
            return redirect(url_for('auth.register'))

        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO authors (name, password, email) VALUES (%s, %s, %s)', (name, password, email))
        db.commit()
        return redirect(url_for('auth.login'))

    return render_template('users/register.html', page_title="Register User")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cur = get_db().cursor()
        cur.execute('SELECT * FROM authors WHERE email = %s', (email,))
        user = cur.fetchone()

        if user and check_password_hash(user['password'], password):
            session['id'] = user['id']
            session['user_name'] = user['name']
            session['email'] = user['email']
            session['is_admin'] = user['is_admin']
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

        cur = get_db().cursor()
        cur.execute('SELECT email FROM authors')
        emails = cur.fetchall()

        if email in [e['email'] for e in emails] and email != g.email:
            flash('Email already exists!', 'error')
            return redirect(url_for('auth.profile'))

        if not name or not email:
            flash('Name and email are required!', 'error')
            return redirect(url_for('auth.profile'))

        if password:
            password = generate_password_hash(password)

        db = get_db()
        cur = db.cursor()
        cur.execute('UPDATE authors SET name = %s, email = %s, password = %s WHERE id = %s',
                    (name, email, password, g.user_id))
        db.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    if g.user_id is None:
        flash('You need to be logged in to view your profile.', 'error')
        return redirect(url_for('auth.login'))

    cur = get_db().cursor()
    cur.execute('SELECT * FROM authors WHERE id = %s', (g.user_id,))
    user = cur.fetchone()

    return render_template('users/user_profile.html', page_title="Profile", user=user)


@auth_bp.route('/delete', methods=["GET", "POST"])
def delete_user():
    if g.user_id is None:
        flash('You need to be logged in to delete your account.', 'error')
        return redirect(url_for('auth.login'))

    db = get_db()
    cur = db.cursor()
    cur.execute('DELETE FROM authors WHERE id = %s', (g.user_id,))
    db.commit()

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
        db = get_db()
        cur = db.cursor()
        cur.execute('UPDATE authors SET is_admin = 1 WHERE id = %s', (g.user_id,))
        session['is_admin'] = 1
        db.commit()

        flash('You are now an admin!', 'success')
        return redirect(url_for('blog.posts'))

    return render_template('users/be_admin.html', page_title="Become Admin")