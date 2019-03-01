import flask
from flask import Blueprint, g
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from peewee import IntegrityError, Model
from PIL import Image

# importing related to User & it's forms
from models.user import User, Relationship
from models.post import Post
# from models.relationship import Relationship
from instagram_web.blueprints.users.forms import RegistrationForm, LoginForm, UpdateDetailsForm

# Common import that shares with the posts.py
from flask import render_template, redirect, url_for, flash, request, session, escape
from flask_login import login_user, logout_user, login_required, current_user
from app import app

# import aws_s3 helper
from instagram_web.util.s3_helper import upload_file_to_s3, random_file_name

users_blueprint = Blueprint('users',
							__name__,
							template_folder='templates/users')


# OAuth sections
from flask_dance.contrib.github import make_github_blueprint, github
github_blueprint = make_github_blueprint(client_id='f2bbc19d909797496071', client_secret='3be3e6bd1126a19456e72a1d94882f855b6228f2')
app.register_blueprint(github_blueprint, url_prefix='/github_login')

# Google Auth
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from oauth2client.file import Storage

@users_blueprint.route('/github')
def github_login():
	if not github.authorized:
		return redirect(url_for('github.login'))

	account_info = github.com.get('/user')

	if account_info.ok:
		account_info_json = account_info.json()
		github_username = account_info_json['login']
		flash("Login via Github is successful", 'success')
		return redirect(url_for('users.index'))
	flash('Error occured while logging in via Github', 'danger')
	return redirect(url_for('users.index', username=github_username))
	# github does not allow http -> https
	# need to allow special permission 
	# for linux: "export OAUTHLIB_INSECURE_TRANSPORT=1"
	# for windows: "set OAUTHLIB_INSECURE_TRANSPORT=1"

def redirect_if_logged_in():
	if current_user.is_authenticated:
		flash("You have already been logged in", "warning")
		return redirect(url_for('users.index'))

"""Start of index"""
@users_blueprint.route('/', methods=["GET"])
def index():
	# 1. Search for all posts form current user
	# 2. Search for all posts from followed user
	# 3. Display all the posts from both sources, sorted by date desc
	# Note * Temporarily retrieving from the current user
	posts = Post.select()
	return render_template('index.html', posts=posts)
"""End of index"""

"""
Start of View User Profile
"""
@users_blueprint.route('/<int:user_id>', methods=["GET"])
def display_user(user_id):
	user = User.get_or_none(User.id == user_id)
	posts = Post.select().where(Post.user == user)
	return render_template('user.html', user=user, posts=posts)
"""
End of View User Profile
"""


"""
Start of Register User
"""
@users_blueprint.route('/register', methods=['GET'])
def display_register():
	redirect_if_logged_in()
	form = RegistrationForm()
	return render_template('register.html', register_form=form)

@users_blueprint.route('/register', methods=['POST'])
def register_user():
	form = RegistrationForm()
	if form.validate_on_submit():
		try:
			new_user = User(
				username=form.data['username'],
				email=form.data['email'],
				password=generate_password_hash(form.data['password'])
			)
			new_user.save()
			flash("Thanks for registering", "success")
			return redirect(url_for('users.display_login'))
		except IntegrityError:
			flash('Duplication of either username or email', 'warning')
	return render_template('register.html', register_form=form)
"""
End of Register User
"""

"""
Start of Login User
"""
@users_blueprint.route('/login', methods=['GET'])
def display_login():
	redirect_if_logged_in()
	form = LoginForm()
	return render_template('login.html', login_form=form)

@users_blueprint.route('/login', methods=['POST'])
def log_user():
	form = LoginForm()
	next_page = request.args.get('next')
	if form.validate_on_submit():
		user = User.get_or_none(User.email == form.data['email'])
		if user != None:
			password = check_password_hash(user.password, form.password.data)
			if password:
				login_user(user)
				flash("You've been logged in!", "success")
				if next_page:
					return redirect(url_for(next_page))
				else:
					return redirect(url_for('users.index'))
			else:
				flash("Please recheck the password entered", "warning")
		else:
			flash("There is no account associated with the particular address", "danger")
	return render_template('login.html', login_form=form)
"""
End of Login User
"""


"""
Start of Update User
"""
@users_blueprint.route('/update', methods=['GET'])
def display_update():
	form = UpdateDetailsForm()
	form.username.data = current_user.username
	form.email.data = current_user.email
	post_count = Post.select().where(Post.user == current_user)
	followers_count = current_user.followers()
	following_count = current_user.following()
	return render_template('update.html', form=form, username=current_user.username, email=current_user.email, post_count=post_count, followers_count=followers_count, following_count=following_count)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# temporarily allow posting of image
# suppose to update profile
@users_blueprint.route('/update', methods=['POST'])
@login_required
def update_user():
	form = UpdateDetailsForm()
	username_test = User.get_or_none(User.username == form.username.data)
	email_test = User.get_or_none(User.email == form.email.data)
	# A
	if "picture" not in request.files:
		flash("No picture key in request.files", 'danger')
		return redirect(url_for('users.update_user'))
	# B
	file = request.files['picture']
	# C
	if file.filename == '':
		flash("Please select a file", 'danger')
		return redirect(url_for('users.update_user'))
	# D
	if file and allowed_file(file.filename):
		file.filename = secure_filename(file.filename)
		output = upload_file_to_s3(file, app.config['S3_BUCKET'])
		# print(output)
		current_user.image_file = output
		# current_user.save()
		try:
			updated_user = User(
				username=form.username.data,
				email=form.email.data,
				password=generate_password_hash(form.password.data),
				picture=output
			)
		except IntegrityError:
			flash('Duplication of either username or email', 'warning')
		else:
			updated_user.save() # does this create new or update??
			flash('Data saved', 'success')
			# if username_test == None and email_test == None:
			# else:
			# 	flash('Duplication of either username or email', 'warning')
		return redirect(url_for('users.index'))
	else:
		return redirect("/")
	# 	# meant for the condition of success
"""
End of Update User
"""

@users_blueprint.route('/logout')
@login_required
def logout():
	logout_user()
	flash("You've been logged out!", "success")
	return redirect(url_for('users.index'))

"""
Google Auth
"""

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
	flask.session[AUTH_STATE_KEY] = state
	session.permanent = True
	return redirect(uri, code=302)

@users_blueprint.route('/google/auth')
def google_auth_redirect():
	state = request.args.get('state', default=None, type=None)
	session = OAuth2Session(app.config['GOOGLE_CLIENT_ID'], app.config['GOOGLE_CLIENT_SECRET'], scope=app.config['GOOGLE_AUTHORIZATION_SCOPE'], state=state, redirect_uri=url_for('users.index'))
	oauth2_tokens = session.fetch_access_token(ACCESS_TOKEN_URI, authorization_response=request.url)
	flask.session[AUTH_TOKEN_KEY] = oauth2_tokens
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

"""
Following and Unfollow Users
"""
@users_blueprint.route('/follow/<string:username>')
@login_required
def follow(username):
	try:
		to_user = User.get(User.username**username)
	except User.DoesNotExist:
		pass
	else:
		try:
			Relationship.create(
				from_user=current_user,
				to_user=to_user
			)
		except IntegrityError:
			pass
		else:
			flash(f"You're now following {to_user.username}", "success")
	return redirect(url_for('index', username=to_user.username))

@users_blueprint.route('/unfollow/<string:username>')
@login_required
def unfollow(username):
	try:
		to_user = User.get(User.username**username)
	except User.DoesNotExist:
		try:
			Relationship.get(
				from_user=current_user,
				to_user=to_user
			).delete_instance()
		except IntegrityError:
			pass
		else:
			flash(f"You have now unfollowed {to_user.username}", "warning")
	return redirect(url_for('index', username=to_user.username))