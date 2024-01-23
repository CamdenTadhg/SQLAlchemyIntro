from unittest import TestCase

from app import app
from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Tests for user model."""

    def setUp(self):
        """Clean up any existing users."""

        User.query.delete()

    def tearDown(self):
        """Clean up any fouled transactions."""

        db.session.rollback()

    def test_get_full_name(self):
        user = User(first_name="Camden", last_name="Tadhg")
        self.assertEqual(user.get_full_name(), "Camden Tadhg")