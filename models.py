from db import db

post_like = db.Table('post_like',
    db.Column('author_id', db.Integer, db.ForeignKey('author.id', ondelete='CASCADE'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), primary_key=True)
)

comment_like = db.Table('comment_like',
    db.Column('author_id', db.Integer, db.ForeignKey('author.id', ondelete='CASCADE'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), primary_key=True)
)
class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Integer, default=0)

    # Cascade all operations: save-update, merge, delete, and orphan removal
    posts = db.relationship(
        'Post',
        backref='author',
        lazy=True,
        cascade="all, delete-orphan"
    )
    posts_liked = db.relationship(
        'Post',
        secondary='post_like',
        backref='liked_by',
        lazy=True
    )
    comments_liked = db.relationship(
        'Comment',
        secondary='comment_like',
        backref='liked_by',
        lazy=True
    )


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    # Foreign Key with DB-level cascade
    author_id = db.Column(
        db.Integer,
        db.ForeignKey('author.id', ondelete='CASCADE'),
        nullable=False
    )

    author_name = db.Column(db.String(100), nullable=False)

    # Cascade so deleting a post deletes all comments
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy=True,
        cascade="all, delete-orphan"
    )
    


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False )
    likes = db.Column(db.Integer, default=0)

    # Foreign Keys with DB-level cascade
    post_id = db.Column(
        db.Integer,
        db.ForeignKey('post.id', ondelete='CASCADE'),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('author.id', ondelete='CASCADE'),
        nullable=False
    )

    user_name = db.Column(db.String(100), nullable=False)

    # Relationships with backref
    user = db.relationship('Author', backref='user_comments')