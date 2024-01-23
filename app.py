"""Blogly application."""

from flask import Flask
from models import db, connect_db, User
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "secret"

debug=DebugToolbarExtension(app)

connect_db(app)
db.create_all()



## create flask app
## make a base template
## make a user listing page
## make a new user form page
## make a user detail page
## make an edit user page
## make all routes
## add testing
## create and add full name method
## list users in order by last_name, first_name
## turn full name into a property