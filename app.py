"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash
from models import db, connect_db, User, Post, Tag, PostTag
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

@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404

#USER ROUTES
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
    if first_name == '':
        flash('No first name entered', 'error')
        return redirect('/users/new')
    last_name = request.form["last-name"]
    if last_name == '':
        flash('No last name entered', 'error')
        return redirect('/users/new')
    if request.form["image-url"]:
        image_url = request.form["image-url"]
    else:
        image_url = 'https://static.vecteezy.com/system/resources/previews/002/318/271/original/user-profile-icon-free-vector.jpg'
    new_user = User(first_name = first_name, last_name = last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()
    flash('New user created', 'success')
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
    if first_name == '':
        flash('No first name entered', 'error')
        return redirect(f'/users/{user_id}/edit')
    last_name = request.form["last-name"]
    if last_name == '':
        flash('No last name entered', 'error')
        return redirect(f'/users/{user_id}/edit')
    image_url = request.form["image-url"]
    if image_url == '':
        image_url = 'https://static.vecteezy.com/system/resources/previews/002/318/271/original/user-profile-icon-free-vector.jpg'
    user = User.query.get_or_404(user_id)
    user.first_name = first_name
    user.last_name = last_name
    user.image_url = image_url
    db.session.add(user)
    db.session.commit()
    flash('User profile saved', 'success')
    return redirect('/users')

@app.route('/users/<user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """deletes user from the database"""
    u=User.query.get(user_id)
    db.session.delete(u)
    db.session.commit()
    flash('User profile deleted', 'success')
    return redirect('/users')

#POST ROUTES

@app.route('/posts')
def show_posts():
    """shows all posts"""
    posts = db.session.execute(db.select(Post).order_by(Post.created_at.desc())).scalars()
    return render_template('posts.html', posts=posts)

@app.route('/users/<user_id>/posts/new')
def show_new_post_form(user_id):
    """shows a form for adding a new post"""
    user = User.query.get_or_404(user_id)
    tags = db.session.execute(db.select(Tag).order_by(Tag.name)).scalars()
    return render_template("newpost.html", user=user, tags=tags)

@app.route('/users/<user_id>/posts/new', methods=["POST"])
def add_post(user_id):
    """adds new post to appropriate user"""
    title = request.form['title']
    if title == '':
        flash('No title added', 'error')
        return redirect(f'/users/{user_id}/posts/new')
    content = request.form['content']
    if content == '':
        flash('No content added', 'error')
        return redirect(f'/users/{user_id}/posts/new')
    new_post = Post(title = title, content = content, created_at = datetime.now(), user_id = user_id)
    db.session.add(new_post)
    db.session.commit()
    tags = request.form.getlist('tag')
    for tag in tags: 
        print('************')
        print(tag)
        print('**************')
        current_tag = db.session.query(Tag).filter(Tag.name == tag).first()
        new_post.tags.append(current_tag)
        db.session.add(new_post)
        db.session.commit()
    flash('New post added', 'success')
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
    tags = db.session.execute(db.select(Tag).order_by(Tag.name)).scalars()
    return render_template('postedit.html', post=post, tags=tags)

@app.route('/posts/<post_id>/edit', methods=["POST"])
def edit_post(post_id):
    title = request.form['title']
    if title == '':
        flash('No title added', 'error')
        return redirect(f'/posts/{post_id}/edit')
    content = request.form['content']
    if content == '':
        flash('No content added', 'error')
        return redirect(f'/posts/{post_id}/edit')
    post = Post.query.get_or_404(post_id)
    post.title = title
    post.content = content
    db.session.add(post)
    db.session.commit()
    PostTag.query.filter_by(post_id=post_id).delete()
    db.session.commit()
    tags = request.form.getlist('tag')
    for tag in tags:
        current_tag = db.session.query(Tag).filter(Tag.name == tag).first()
        post.tags.append(current_tag)
        db.session.add(post)
        db.session.commit()
    flash('Post changes saved', 'success')
    return redirect(f'/posts/{post_id}')

@app.route('/posts/<post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """deletes post"""
    post = Post.query.get_or_404(post_id)
    user = post.user
    p = Post.query.get(post_id)
    db.session.delete(p)
    db.session.commit()
    flash('Post deleted', 'success')
    return redirect(f'/users/{user.id}')

#TAG ROUTES

@app.route('/tags')
def show_tags():
    """shows all tags"""
    tags = db.session.execute(db.select(Tag).order_by(Tag.name)).scalars()
    return render_template('tags.html', tags=tags)

@app.route('/tags/<tag_id>')
def show_tag(tag_id):
    """shows an individual tag and the associated posts"""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tagdetail.html', tag=tag)

@app.route('/tags/new')
def show_new_tag_form():
    """shows a form for adding a new tag"""
    posts = db.session.execute(db.select(Post).order_by(Post.created_at)).scalars()
    return render_template("newtag.html", posts=posts)

@app.route('/tags/new', methods=["POST"])
def add_tag():
    """adds new tag to database"""
    name = request.form['name']
    if name == '':
        flash('No name added', 'error')
        return redirect('/tags/new')
    new_tag = Tag(name= name)
    db.session.add(new_tag)
    db.session.commit()
    posts = request.form.getlist('post')
    for post in posts:
        current_post = db.session.query(Post).filter(Post.title == post).first()
        new_tag.posts.append(current_post)
        db.session.add(new_tag)
        db.session.commit()
    flash('New tag added', 'success')
    return redirect('/tags')

@app.route('/tags/<tag_id>/edit')
def show_tag_edit_form(tag_id):
    "shows the form for editing a tag"
    tag = Tag.query.get_or_404(tag_id)
    posts = db.session.execute(db.select(Post).order_by(Post.created_at)).scalars()
    return render_template('tagedit.html', tag=tag, posts=posts)

@app.route('/tags/<tag_id>/edit', methods=["POST"])
def edit_tag(tag_id):
    name = request.form['name']
    if name == '':
        flash('No name added', 'error')
        return redirect(f'/tags/{tag_id}/edit')
    tag = Tag.query.get_or_404(tag_id)
    tag.name = name
    db.session.add(tag)
    db.session.commit()
    PostTag.query.filter_by(tag_id=tag_id).delete()
    db.session.commit()
    posts = request.form.getlist('post')
    for post in posts:
        current_post = db.session.query(Post).filter(Post.title == post).first()
        tag.posts.append(current_post)
        db.session.add(tag)
        db.session.commit()
    flash('Tag changes saved', 'success')
    return redirect(f'/tags/{tag_id}')

@app.route('/tags/<tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    """deletes tag"""
    t = Tag.query.get(tag_id)
    db.session.delete(t)
    db.session.commit()
    flash('Tag deleted', 'success')
    return redirect('/tags')


# 1 style site appropriately
