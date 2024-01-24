"""Blogly application."""

from flask import Flask, request, render_template, redirect
from models import db, connect_db, User, Post
from flask_debugtoolbar import DebugToolbarExtension

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
    """redirects to user list"""
    return redirect('/users')

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
    image_url = request.form["image-url"]
    new_user = User(first_name = first_name, last_name = last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<user_id>')
def show_user(user_id):
    """shows details of a user"""
    user = User.query.get_or_404(user_id)
    posts = db.session.execute(db.select(Post).where(user_id == user_id)).scalars()
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


# revise user detail page
# create new post form
# create edit post form
# create post detail form
# create routes
# update & add tests
# make a homepage that shows 5 most recent posts
# show friendly date
# notify user of form errors and sucecessful submissions
# add a custom 404 error page
# cascade deletion of users