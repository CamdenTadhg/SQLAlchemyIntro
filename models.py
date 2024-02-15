"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model for blogly app"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.Text, nullable=False, default='https://static.vecteezy.com/system/resources/previews/002/318/271/original/user-profile-icon-free-vector.jpg')

    posts = db.relationship('Post', back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        """show info about a user"""
        user = self
        return f"<User {user.id} {user.first_name} {user.last_name}>"
    
    @property
    def full_name(self):
        """return the full name of the user"""
        return f"{self.first_name} {self.last_name}"
    
class Post(db.Model):
    """Post model for blogly app"""

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', back_populates="posts")

    def __repr__(self):
        """show info about a post"""
        return f"<Post {self.id} {self.title} {self.user_id}>"
    
    @property
    def nice_date(self):
        """Return a nicely formatted date"""
        return self.created_at.strftime('%a %m %d %Y, %I:%M %p')
    
class Tag(db.Model):
    """Tag model for blogly app"""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    posts = db.relationship('Post', secondary='posts_tags', backref='tags')

    def __repr__(self):
        """show info about a tag"""
        return f"<Tag {self.id} {self.name}>"
    
class PostTag(db.Model):
    """PostTag model for blogly app"""

    __tablename__ = "posts_tags"

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
