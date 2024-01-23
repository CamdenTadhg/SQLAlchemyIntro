from unittest import TestCase

from app import app
from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class BloglyViewsTestCase(TestCase):
    """Tests for views for Blogly app."""

    def setUp(self):
        """Add sample user."""

        User.query.delete()

        user = User(first_name="Jane", last_name="Doe", image_url='/static/user-profile-icon.png')
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.user = user

    def tearDown(self):
        """Clean up any fouled transactions."""

        db.session.rollback()

    def test_redirection(self):
        with app.test_client() as client:
            resp = client.get('/')
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/users')

    def test_redirection_followed(self):
        with app.test_client() as client: 
            resp = client.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)

    def test_show_user_list(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Jane Doe', html)

    def test_show_add_form(self):
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create a user', html)
    
    def test_add_user(self):
        with app.test_client() as client:
            resp = client.post('/users/new', data={'first-name': 'Camden', 'last-name': 'Tadhg', 'image-url':'https://www.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/users')
            self.assertEqual(str(User.query.get(2)), '<User 2 Camden Tadhg>')
    
    def test_add_user_redirect(self):
        with app.test_client() as client:
            resp = client.post('/users/new', data={'first-name': 'Camden', 'last-name': 'Tadhg', 'image-url':'https://www.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Camden Tadhg', html)

    def test_show_user(self):
        with app.test_client() as client:
            test_user = User.query.filter_by(first_name="Jane").first()
            user_id = test_user.id
            resp = client.get(f'/users/{user_id}')
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Jane Doe', html)

    def test_show_edit_form(self):
        with app.test_client() as client:
            test_user = User.query.filter_by(first_name="Jane").first()
            user_id = test_user.id
            resp = client.get(f'/users/{user_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit a user', html)

    def test_edit_user(self):
        with app.test_client() as client:
            test_user = User.query.filter_by(first_name="Jane").first()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/edit', data={'first-name': 'John', 'last-name': 'Doe', 'image-url':'/static/user-profile-icon.png' })
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/users')
            self.assertEqual(str(User.query.get(user_id)), f'<User {user_id} John Doe>')
    
    def test_edit_user_redirect(self):
        with app.test_client() as client:
            test_user = User.query.filter_by(first_name="Jane").first()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/edit', data={'first-name': 'John', 'last-name': 'Doe', 'image-url':'/static/user-profile-icon.png' }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('John Doe', html)

    def test_delete_user(self):
        with app.test_client() as client:
            resp = client.post('/users/1/delete')
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/users')

    def test_delete_user(self):
        with app.test_client() as client:
            test_user = User.query.filter_by(first_name="Jane").first()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Jane Doe', html)