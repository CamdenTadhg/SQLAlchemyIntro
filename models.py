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
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime('%a %m %d %Y, %H:%M %p'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', backref="posts")

    def __repr__(self):
        """show info about a post"""
        return f"<Post {self.id} {self.title} {self.user_id}>"
    

        # for post in posts:
        # timestamp = str(post.created_at)
        # d = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        # s = d.strftime('%a %m %d %Y, %H:%M %p')
        # post.created_at = s