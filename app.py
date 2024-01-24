"""Blogly application."""

from flask import Flask, request, render_template, redirect
from models import db, connect_db, User, Post
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug=DebugToolbarExtension(app)

app.app_context().push()

connect_db(app)
db.create_all()

@app.route('/')
def home_page():
    """home page displays 5 most recent posts"""
    posts = db.session.execute(db.select(Post).order_by(Post.created_at.desc()).limit(5)).scalars()
    return render_template("home.html", posts=posts)

@app.route('/users')
def show_user_list():
    """shows a list of all site users"""
    users = db.session.execute(db.select(User).order_by(User.last_name, User.first_name)).scalars()
    return render_template("users.html", users=users)

@app.route('/users/new')
def show_add_form():
    """shows a form for adding new users"""
    return render_template("newuser.html")

@app.route('/users/new', methods=["POST"])
def add_user():
    """adds user to the database"""
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    if request.form["image-url"]:
        image_url = request.form["image-url"]
    else:
        image_url = 'https://static.vecteezy.com/system/resources/previews/002/318/271/original/user-profile-icon-free-vector.jpg'
    new_user = User(first_name = first_name, last_name = last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<user_id>')
def show_user(user_id):
    """shows details of a user"""
    user = User.query.get_or_404(user_id)
    posts = db.session.execute(db.select(Post).where(Post.user_id == user_id)).scalars()
    return render_template('userdetail.html', user=user, posts=posts)

@app.route('/users/<user_id>/edit')
def show_edit_form(user_id):
    """shows a form for editing user information"""
    user=User.query.get_or_404(user_id)
    return render_template("useredit.html", user=user)

@app.route('/users/<user_id>/edit', methods=["POST"])
def edit_user(user_id):
    """edits user information in the database"""
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]
    user = User.query.get_or_404(user_id)
    user.first_name = first_name
    user.last_name = last_name
    user.image_url = image_url
    db.session.add(user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """deletes user from the database"""
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return redirect('/users')

@app.route('/users/<user_id>/posts/new')
def show_new_post_form(user_id):
    """shows a form for adding a new post"""
    user = User.query.get_or_404(user_id)
    return render_template("newpost.html", user=user)

@app.route('/users/<user_id>/posts/new', methods=["POST"])
def add_post(user_id):
    """adds new post to appropriate user"""
    title = request.form['title']
    content = request.form['content']
    new_post = Post(title = title, content = content, created_at = datetime.now(), user_id = user_id)
    db.session.add(new_post)
    db.session.commit()
    return redirect(f'/users/{user_id}')

@app.route('/posts/<post_id>')
def show_post(post_id):
    """shows an individual post"""
    post = Post.query.get_or_404(post_id)
    user = post.user
    return render_template('postdetail.html', post=post, user=user)

@app.route('/posts/<post_id>/edit')
def show_post_edit_form(post_id):
    "shows the form for editing a post"
    post = Post.query.get_or_404(post_id)
    return render_template('postedit.html', post=post)

@app.route('/posts/<post_id>/edit', methods=["POST"])
def edit_post(post_id):
    title = request.form['title']
    content = request.form['content']
    post = Post.query.get_or_404(post_id)
    post.title = title
    post.content = content
    db.session.add(post)
    db.session.commit()
    return redirect(f'/posts/{post_id}')

@app.route('/posts/<post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """deletes post"""
    post = Post.query.get_or_404(post_id)
    user = post.user
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()
    return redirect(f'/users/{user.id}')


# 5 make a homepage that shows 5 most recent posts
# 4 show friendly date
# 3 notify user of form errors and sucecessful submissions
# 2 add a custom 404 error page
# 1 cascade deletion of users
# 0 run all tests again then refill database