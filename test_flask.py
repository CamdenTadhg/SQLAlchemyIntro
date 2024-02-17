from unittest import TestCase

from app import app
from models import db, User, Post, Tag, PostTag

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class BloglyViewsTestCase(TestCase):
    """Tests for views for Blogly app."""

    def setUp(self):
        """Add sample user and sample post."""

        PostTag.query.delete()
        Post.query.delete()
        Tag.query.delete()
        User.query.delete()
        
        user = User(first_name="Jane", last_name="Doe")
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.user = user

        post = Post(title="test post test", content="test post content", user_id = user.id)
        db.session.add(post)
        db.session.commit()

        tag = Tag(name="testing")
        db.session.add(tag)
        db.session.commit()

        post_tag=PostTag(post_id = post.id, tag_id=tag.id)
        db.session.add(post_tag)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transactions."""

        db.session.rollback()

    def test_home_page(self):
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Blogly Recent Posts', html)

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
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Camden')).scalar()
            user_id = test_user.id


            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/users')
            self.assertEqual(str(User.query.get(user_id)), f'<User {user_id} Camden Tadhg>')
    
    def test_add_user_redirect(self):
        with app.test_client() as client:
            resp = client.post('/users/new', data={'first-name': 'Camden', 'last-name': 'Tadhg', 'image-url':'https://www.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Camden Tadhg', html)

    def test_show_user(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.get(f'/users/{user_id}')
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Jane Doe', html)
            self.assertIn('test post test', html)

    def test_show_edit_form(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.get(f'/users/{user_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit a user', html)

    def test_edit_user(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/edit', data={'first-name': 'John', 'last-name': 'Doe', 'image-url':'/static/user-profile-icon.png' })
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/users')
            self.assertEqual(str(User.query.get(user_id)), f'<User {user_id} John Doe>')
    
    def test_edit_user_redirect(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/edit', data={'first-name': 'John', 'last-name': 'Doe', 'image-url':'/static/user-profile-icon.png' }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('John Doe', html)

    def test_delete_user(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            resp = client.post(f'/users/{test_user.id}/delete')
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/users')

    def test_delete_user_redirect(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Jane Doe', html)

    def test_show_posts(self):
        with app.test_client() as client:
            resp = client.get('/posts')
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test post test', html)
            self.assertIn('testing', html)

    def test_show_new_post_form(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.get(f'/users/{user_id}/posts/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create a new post', html)

    def test_add_post(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/posts/new', data={'title': 'test post 2', 'content': 'this is a second test post'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user_id}')
            self.assertEqual(str(Post.query.get(2)), f'<Post 2 test post 2 {user_id}>')

    def test_add_post_redirect(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/posts/new', data={'title': 'test post 2', 'content': 'This is a second test post', 'tag': ['testing']}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test post 2', html)
            self.assertIn('testing', html)
    
    def test_show_post(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id
            resp = client.get(f'/posts/{post_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test post test', html)
            self.assertIn('Jane Doe', html)
            self.assertIn('testing', html)

    def test_show_post_edit_form(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id
            resp = client.get(f'/posts/{post_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit a post', html)
    
    def test_edit_post(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id    
            resp = client.post(f'/posts/{post_id}/edit', data={'title':'edited test post', 'content':'test post content'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/posts/{post_id}')
            self.assertEqual(str(Post.query.get(post_id)), f'<Post {post_id} edited test post {test_post.user.id}>')
    
    def test_edit_post_redirect(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id  
            resp = client.post(f'/posts/{post_id}/edit', data={'title':'edited test post', 'content':'test post content', 'tag': []}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('edited test post', html)
            self.assertNotIn('testing', html)
    
    def test_delete_post(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id
            user = test_post.user
            resp = client.post(f'/posts/{post_id}/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user.id}')

    def test_delete_post_redirect(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id
            resp = client.post(f'/posts/{post_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('test post test', html)
    
    def test_no_first_name(self):
        with app.test_client() as client:
            resp = client.post('/users/new', data={'first-name': '', 'last-name': 'Tadhg', 'image-url':'https://www.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png'})


            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/users/new')

    def test_no_first_name_redirect(self):
        with app.test_client() as client:
            resp = client.post('/users/new', data={'first-name': '', 'last-name': 'Tadhg', 'image-url':'https://www.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('No first name', html)
    
    def test_no_last_name(self):
        with app.test_client() as client:
            resp = client.post('/users/new', data={'first-name': 'Camden', 'last-name': '', 'image-url':'https://www.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/users/new')
    
    def test_no_last_name_redirect(self):
        with app.test_client() as client:
            resp = client.post('/users/new', data={'first-name': 'Camden', 'last-name': '', 'image-url':'https://www.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('No last name', html)

    def test_edit_no_first_name(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/edit', data={'first-name': '', 'last-name': 'Doe', 'image-url':'/static/user-profile-icon.png' })
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user_id}/edit')
    
    def test_edit_no_first_name_redirect(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/edit', data={'first-name': '', 'last-name': 'Doe', 'image-url':'/static/user-profile-icon.png' }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('No first name', html)

    def test_edit_no_last_name(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/edit', data={'first-name': 'John', 'last-name': '', 'image-url':'/static/user-profile-icon.png' })
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user_id}/edit')
    
    def test_edit_no_lst_name_redirect(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/edit', data={'first-name': 'John', 'last-name': '', 'image-url':'/static/user-profile-icon.png' }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('No last name', html)

    def test_no_title(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/posts/new', data={'title': '', 'content': 'this is a second test post'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user_id}/posts/new')

    def test_no_title_redirect(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/posts/new', data={'title': '', 'content': 'This is a second test post'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('No title', html)

    def test_no_content(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/posts/new', data={'title': 'test post', 'content': ''})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user_id}/posts/new')

    def test_no_content_redirect(self):
        with app.test_client() as client:
            test_user = db.session.execute(db.select(User).where(User.first_name == 'Jane')).scalar()
            user_id = test_user.id
            resp = client.post(f'/users/{user_id}/posts/new', data={'title': 'test post', 'content': ''}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('No content', html)

    def test_edit_no_title(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id    
            resp = client.post(f'/posts/{post_id}/edit', data={'title':'', 'content':'test post content'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/posts/{post_id}/edit')
    
    def test_edit_no_title_redirect(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id  
            resp = client.post(f'/posts/{post_id}/edit', data={'title':'', 'content':'test post content'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('No title', html)

    def test_edit_no_content(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id    
            resp = client.post(f'/posts/{post_id}/edit', data={'title':'edited test post', 'content':''})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/posts/{post_id}/edit')
    
    def test_edit_no_content_redirect(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            post_id = test_post.id  
            resp = client.post(f'/posts/{post_id}/edit', data={'title':'edited test post', 'content':''}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('No content', html)

    def test_show_tags(self):
        with app.test_client() as client:
            resp = client.get('/tags')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testing', html)

    def test_show_tag(self):
        with app.test_client() as client:
            test_tag = db.session.execute(db.select(Tag).where(Tag.name == 'testing')).scalar()
            tag_id = test_tag.id
            resp = client.get(f'/tags/{tag_id}')
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testing', html)
            self.assertIn('test post test', html)
    
    def test_show_new_tag_form(self):
        with app.test_client() as client:
            resp = client.get('tags/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create a new tag', html)

    def test_add_tag(self):
        with app.test_client() as client:
            resp = client.post('/tags/new', data={'name': 'moretesting'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/tags')

    def test_add_tag_redirect(self):
        with app.test_client() as client:
            test_post = db.session.execute(db.select(Post).where(Post.title == "test post test")).scalar()
            resp = client.post('/tags/new', data={'name': 'moretesting', 'post': ["test post test"]}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('moretesting', html)
            self.assertIn('moretesting', str(test_post.tags))
    
    def test_show_tag_edit_form(self):
        with app.test_client() as client:
            test_tag = db.session.execute(db.select(Tag).where(Tag.name == "testing")).scalar()
            resp = client.get(f'/tags/{test_tag.id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit a tag', html)

    def test_edit_tag(self):
        with app.test_client() as client: 
            test_tag = db.session.execute(db.select(Tag).where(Tag.name == "testing")).scalar()
            resp = client.post(f'/tags/{test_tag.id}/edit', data={'name':'testing'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/tags/{test_tag.id}')

    def test_edit_tag_redirect(self):
        with app.test_client() as client:
            test_tag = db.session.execute(db.select(Tag).where(Tag.name == "testing")).scalar()
            test_post = db.session.execute(db.select(Post).where(Post.title == 'test post test')).scalar()
            resp = client.post(f'/tags/{test_tag.id}/edit', data={'name': 'testing2', 'post': []}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testing2', html)
            self.assertNotIn('testing2', str(test_post.tags))
            
    def test_delete_tag(self):
        with app.test_client() as client:
            test_tag = db.session.execute(db.select(Tag).where(Tag.name == 'testing')).scalar()
            tag_id = test_tag.id
            resp = client.post(f'/tags/{tag_id}/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/tags')

    def test_delete_tag_redirect(self):
        with app.test_client() as client:
            test_tag = db.session.execute(db.select(Tag).where(Tag.name == "testing")).scalar()
            tag_id = test_tag.id
            resp = client.post(f'/tags/{tag_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('testing', html)