from flask import Blueprint, render_template, request, redirect, url_for, flash, g

blog_bp = Blueprint('blog', __name__, template_folder='templates')
from db import get_db


@blog_bp.route('/')
def posts():
    cur = get_db().cursor()
    cur.execute('SELECT * FROM posts')
    posts = cur.fetchall()
    return render_template('posts/posts_html.html', page_title="Posts", posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    if g.user_id is None:
        flash('You need to be logged in to comment.', 'error')
        return redirect(url_for('auth.login'))

    cur = get_db().cursor()

    cur.execute('SELECT * FROM comments WHERE post_id = %s', (post_id,))
    comments = cur.fetchall()

    if request.method == 'POST':
        content = request.form.get('content')

        if not content:
            flash('Content is required!', 'error')
            return redirect(url_for('blog.post', post_id=post_id))

        cur.execute('INSERT INTO comments (post_id, user_name, content, user_id) VALUES (%s, %s, %s, %s)',
                    (post_id, g.user_name, content, g.user_id))
        get_db().commit()

        return redirect(url_for('blog.post', post_id=post_id))

    cur.execute('SELECT * FROM posts WHERE id = %s', (post_id,))
    post = cur.fetchone()

    if post is None:
        return "Post not found", 404

    return render_template('posts/post.html', page_title="Post Details", post=post, author_id=post['author_id'], comments=comments)


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

        cur = get_db().cursor()
        cur.execute('INSERT INTO posts (title, content, author_id, author_name) VALUES (%s, %s, %s, %s)',
                    (title, content, g.user_id, g.user_name))
        get_db().commit()

        return redirect(url_for('blog.posts'))

    return render_template('posts/post_create.html', page_title="Add Post")


@blog_bp.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if g.user_id is None:
        flash('You need to be logged in to edit posts.', 'error')
        return redirect(url_for('auth.login'))

    cur = get_db().cursor()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Title and content are required!', 'error')
            return redirect(url_for('blog.edit_post', post_id=post_id))

        cur.execute('UPDATE posts SET title = %s, content = %s WHERE id = %s',
                    (title, content, post_id))
        get_db().commit()

        flash('Post updated successfully!', 'success')
        return redirect(url_for('blog.post', post_id=post_id))

    cur.execute('SELECT * FROM posts WHERE id = %s', (post_id,))
    post = cur.fetchone()

    return render_template('posts/post_edit.html', page_title="Edit Post", post_id=post_id, post=post)


@blog_bp.route('/posts/my_posts')
def my_posts():
    if g.user_id is None:
        flash('You need to be logged in to view your posts.', 'error')
        return redirect(url_for('auth.login'))

    cur = get_db().cursor()
    cur.execute('SELECT * FROM posts WHERE author_id = %s', (g.user_id,))
    posts = cur.fetchall()

    return render_template('posts/posts_html.html', page_title="My Posts", posts=posts)


@blog_bp.route('/post/delete/comment/<int:comment_id>')
def delete_comment(comment_id):
    cur = get_db().cursor()

    cur.execute('SELECT * FROM comments WHERE id = %s', (comment_id,))
    comment = cur.fetchone()

    if g.user_id is None:
        flash('You need to be logged in to delete comments.', 'error')
        return redirect(url_for('auth.login'))

    if g.user_id != comment['user_id'] and not g.is_admin:
        flash('This is not your comment', 'error')
        return redirect(url_for('blog.post', post_id=comment["post_id"]))

    cur.execute('DELETE FROM comments WHERE id = %s', (comment_id,))
    get_db().commit()

    return redirect(url_for('blog.post', post_id=comment["post_id"]))