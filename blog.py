# blog.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import Post, Comment
from sqlalchemy.exc import IntegrityError
from db import db
blog_bp = Blueprint('blog', __name__, template_folder='templates')


@blog_bp.route('/', methods=['GET', 'POST'])
def posts():
    if request.method == "POST":
        query = request.form.get('query')
        posts = []
        for i in Post.query.all():
            if query.lower() in i.title.lower():
                posts.append(i)
        return render_template('posts/posts_html.html', page_title=query, posts=posts)
    posts = Post.query.all()
    return render_template('posts/posts_html.html', page_title="Posts", posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    if g.user_id is None:
        flash('You need to be logged in to comment.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        content = request.form.get('content')

        if not content:
            flash('Content is required!', 'error')
            return redirect(url_for('blog.post', post_id=post_id))

        comment = Comment(
            content=content,
            post_id=post_id,
            user_id=g.user_id,
            user_name=g.user_name
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('blog.post', post_id=post_id))

    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    return render_template('posts/post.html', page_title="Post Details", post=post, comments=comments)


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

        new_post = Post(title=title, content=content, author_id=g.user_id, author_name=g.user_name)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blog.posts'))

    return render_template('posts/post_create.html', page_title="Add Post")


@blog_bp.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if g.user_id is None:
        flash('You need to be logged in to edit posts.', 'error')
        return redirect(url_for('auth.login'))

    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Title and content are required!', 'error')
            return redirect(url_for('blog.edit_post', post_id=post_id))

        post.title = title
        post.content = content
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('blog.post', post_id=post_id))

    return render_template('posts/post_edit.html', page_title="Edit Post", post=post)


@blog_bp.route('/posts/my_posts')
def my_posts():
    if g.user_id is None:
        flash('You need to be logged in to view your posts.', 'error')
        return redirect(url_for('auth.login'))

    posts = Post.query.filter_by(author_id=g.user_id).all()
    return render_template('posts/posts_html.html', page_title="My Posts", posts=posts)


@blog_bp.route('/post/delete/comment/<int:comment_id>')
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if g.user_id is None:
        flash('You need to be logged in to delete comments.', 'error')
        return redirect(url_for('auth.login'))

    if g.user_id != comment.user_id and not g.is_admin:
        flash('This is not your comment', 'error')
        return redirect(url_for('blog.post', post_id=comment.post_id))

    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('blog.post', post_id=comment.post_id))

