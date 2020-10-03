
from flask import redirect, url_for
from flask_wtf import CsrfProtect
from flask import Flask, render_template, flash, request
from flask import current_app
from flask_login import UserMixin
from flask_login import (   LoginManager,current_user, login_required, login_user, logout_user
)
import json

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired

from oauthlib.oauth2 import WebApplicationClient

from db import get_db, insert, delete, select
from db import init_db_command

import praw
import requests
import os 

#use oauth2 with http
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#class MyForm(FlaskForm):
#    name = StringField('name', validators=[DataRequired()])

GOOGLE_CLIENT_ID = '431275871549-g4o4d872ef4nfaincuk42ciongsmlpb9.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'Oruxt-JkQRKI6lWmBRRbJfOV'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


FREQUENCES = [(1,'DAILY'), (2,'WEEKLY') , (3,'MONTHLY')]

class User(UserMixin):
    def __init__(self,  id, name, email, profile_pic):
        self.id = id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

        user = cursor.fetchone()
        if not user:
            return None
    
        user = User(
            id=user[0], name=user[1], email=user[2], profile_pic=user[3]
        )
        return user
    
    @staticmethod
    def create(id_, name, email, profile_pic):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email, profile_pic) "
            "VALUES (%s, %s, %s, %s)",
            (id_, name, email, profile_pic),
        )
        #autocommit true
        #db.commit()
        

class RowForm(FlaskForm):
    subreddit = StringField()
    frequence = SelectField( coerce=int,choices=FREQUENCES)
  

class RedditForm(FlaskForm):
    courses = FieldList(FormField(RowForm), min_entries=0, max_entries=10)
    submit = SubmitField('Sign In')
    # Any other fields can go here (e.g., user_id).

csrf = CsrfProtect()

app = Flask(__name__)
 
app.config['SECRET_KEY'] = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

csrf.init_app(app)

print("init db")
init_db_command()


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
#        return (
#            "<p>Hello, {}! You're logged in! Email: {}</p>"
#            "<div><p>Google Profile Picture:</p>"
#            '<img src="{}" alt="Google profile pic"></img></div>'
#            '<a class="button" href="/logout">Logout</a>'.format(
#                current_user.name, current_user.email, current_user.profile_pic
#            )
#        
        print("user login: ", current_user.name)
        form = RedditForm()
            

        if not form.is_submitted(): 
            records = select(current_user.id)
            print("user records ", records)
            for row in records:
                if len(row)==2:
                    rowform = RowForm()
                    rowform.subreddit=row[0]
                    if (row[1]=='DAILY'):
                        rowform.frequence='1'
                    if (row[1]=='WEEKLY'):
                        rowform.frequence='2'
                    if (row[1]=='MONTHLY'):
                        rowform.frequence='3'
                    
                    form.courses.append_entry(data=rowform)

            rowform = RowForm()
            rowform.subreddit=''
            rowform.frequence='1'
            form.courses.append_entry(data=rowform)


        else:
            print ("submitted")

            if form.validate():
                print ("valid")
            else:
                print("errors:" ,form.errors)

            if form.validate_on_submit():
                delete(current_user.id)
                for course in  form.courses:
                    if (course.subreddit.data):
                        insert(current_user.id, str(course.subreddit.data), FREQUENCES[course.frequence.data-1][1])
    
                flash('Hello ')
            else:
                flash('All the form fields are required. ')

    else:
        return '<a class="button" href="/login">Google Login</a>'


    #return redirect('/')
    return render_template("index.html", title='Index', form=form)



@app.route("/weekly", methods=['GET', 'POST'])
def weeklybest():

    reddit = praw.Reddit(client_id='ht8QzT_L3KMakw',
                     client_secret='MbVz2C3C3K1ENsAe2CExci8RYXw',
                     user_agent='reddit-on-tap')

    records = select(current_user.id)
    for rec in records:
        if len(rec)==2:
            print("*****************"+rec[0])
            sub = rec[0]
            subreddit = reddit.subreddit(sub)
            tops = subreddit.top(limit=10)
            for top in tops:
                print("==>" + top.author.name + " " + top.name + " " + top.selftext)
                     

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided by Google
    user = User(
        id=unique_id, name=users_name, email=users_email, profile_pic=picture
    )


    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

    
