from flask import Blueprint
from models.user import User
from models.post import Post

from flask import render_template, redirect, url_for, flash, request, session, escape
from flask_login import login_user, logout_user, login_required, current_user
from app import app

users_blueprint = Blueprint('users',
							__name__,
							template_folder='templates/users')

from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from oauth2client.file import Storage

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTHORIZATION_SCOPE ='openid email profile'

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'
USER_INFO_KEY = 'user_info'

@users_blueprint.route('/google/login')
def google_login():
	session = OAuth2Session(app.config['GOOGLE_CLIENT_ID'], app.config['GOOGLE_CLIENT_SECRET'], scope=app.config['GOOGLE_AUTHORIZATION_SCOPE'], redirect_uri=url_for('users.index'))
	uri, state = session.authorization_url(AUTHORIZATION_URL)
	session[AUTH_STATE_KEY] = state
	session.permanent = True
	return redirect(uri, code=302)

@users_blueprint.route('/google/auth')
def google_auth_redirect():
	state = request.args.get('state', default=None, type=None)
	session = OAuth2Session(app.config['GOOGLE_CLIENT_ID'], app.config['GOOGLE_CLIENT_SECRET'], scope=app.config['GOOGLE_AUTHORIZATION_SCOPE'], state=state, redirect_uri=url_for('users.index'))
	oauth2_tokens = session.fetch_access_token(ACCESS_TOKEN_URI, authorization_response=request.url)
	session[AUTH_TOKEN_KEY] = oauth2_tokens
	return redirect(url_for('users.index'))

def build_credentials():
	oauth2_tokens = session[AUTH_TOKEN_KEY]
	return google.oauth2.credentials.Credentials(
		oauth2_tokens['access_token'],
		refresh_token=oauth2_tokens['refresh_token'],
		client_id=app.config['GOOGLE_CLIENT_ID'],
		client_secret=app.config['GOOGLE_CLIENT_SECRET'],
		token_uri=ACCESS_TOKEN_URI
	)

def get_user_info():
	credentials = build_credentials()
	oauth2_client = googleapiclient.discovery.build('oauth2', 'v2', credentials=credentials)
	return oauth2_client.userinfo().get().execute()

def store_user_info():
	user = get_user_info()
	storage = Storage()
	storage.put(user)
	# How to determine whether the user has signed up with us?
	# How to save the user credentials inside the database?
	credentials = storage.get()
	# What is the purpose of the line above?? For login?