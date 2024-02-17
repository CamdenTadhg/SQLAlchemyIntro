from unittest import TestCase

from app import app
from models import db, User, Post
from datetime import datetime, date


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Tests for user model."""

    def setUp(self):
        """Clean up any existing users."""

        # User.query.delete()

    def tearDown(self):
        """Clean up any fouled transactions."""

        db.session.rollback()

    def test_full_name(self):
        user = User(first_name="Camden", last_name="Tadhg")
        self.assertEqual(user.full_name, "Camden Tadhg")
    
    def test_nice_date(self):
        user = User(first_name="Camden", last_name="Tadhg")
        db.session.add(user)
        db.session.commit()
        test_user = db.session.execute(db.select(User).where(User.first_name == 'Camden')).scalar()
        user_id=test_user.id
        post = Post(title="test", content="test", created_at=datetime.now(), user_id=user_id)
        self.assertEqual(post.nice_date, "Thr 02 15 2024, 08:55 AM")