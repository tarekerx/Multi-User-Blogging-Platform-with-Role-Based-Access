from flask import Blueprint, render_template, request, redirect, url_for, flash, g


blog_bp = Blueprint('blog', __name__, template_folder='templates')
from db import get_db

@blog_bp.route('/')
def posts():
    db = get_db()
    posts = db.execute('SELECT * FROM posts')
    return render_template('posts/posts_html.html', page_title="Posts", posts=posts)


@blog_bp.route('/post/<int:post_id>')
def post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post is None:
        return "Post not found", 404
    return render_template('posts/post.html', page_title="Post Details", post=post, author_id=post['author_id'])


@blog_bp.route('/post/create', methods=['GET', 'POST'])
def create_post():
    if g.user_id is None:
        flash('You need to be logged in to create posts.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Title and content are required!', 'error')
            return redirect(url_for('blog.create_post'))

        db = get_db()
        db.execute('INSERT INTO posts (title, content, author_id, author_name) VALUES (?, ?, ?, ?)', 
                   (title, content, g.user_id, g.user_name))
        db.commit()
        return redirect(url_for('blog.posts'))

    return render_template('posts/post_create.html', page_title="Add Post")


@blog_bp.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    db = get_db()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Title and content are required!', 'error')
            return redirect(url_for('blog.edit_post', post_id=post_id))

        db.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', 
                   (title, content, post_id))
        db.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('blog.post', post_id=post_id))

    return render_template('posts/post_edit.html', page_title="Edit Post", post_id=post_id,post =db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone())


@blog_bp.route('/posts/my_posts')
def my_posts():
    if g.user_id is None:
        flash('You need to be logged in to view your posts.', 'error')
        return redirect(url_for('auth.login'))

    db = get_db()
    posts = db.execute('SELECT * FROM posts WHERE author_id = ?', (g.user_id,)).fetchall()
    return render_template('posts/posts_html.html', page_title="My Posts", posts=posts)

