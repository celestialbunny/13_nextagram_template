from flask import Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from peewee import IntegrityError
from PIL import Image

# importing related to User & it's forms
from models.user import User
from models.post import Post
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
@users_blueprint.route('/<int:userid>', methods=["GET"])
def display_user(userid):
	user = User.get_or_none(User.id == userid)
	return render_template('user.html', user=user)
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
		breakpoint()
		if user != None:
			breakpoint()
			password = check_password_hash(user.password, form.password.data)
			if password:
				breakpoint()
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
	else:
		flash("Please recheck the login credentials", "warning")
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
	return render_template('update.html', form=form, username=current_user.username, email=current_user.email)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# temporarily allow posting of image
# suppose to update profile
@users_blueprint.route('/update', methods=['POST'])
@login_required
def update_user():
	form = UpdateDetailsForm()
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
		# output_size = (125, 125)
		# file = Image.open(request.files['picture'])
		# i = file.thumbnail(output_size)
		file.filename = secure_filename(file.filename)
		output = upload_file_to_s3(file, app.config['S3_BUCKET'])
		print(output)
		current_user.image_file = output
		current_user.save()
		flash('Data saved', 'success')
		return redirect(url_for('users.index'))
	else:
		return redirect("/")
	# try:
	# 	updated_user = User(
	# 		username=form.username.data,
	# 		email=form.email.data,
	# 		password=generate_password_hash(form.password.data),
	# 		picture=output
	# 	)
	# except IntegrityError:
	# 	flash('Duplication of either username or email', 'warning')
	# else:
	# 	# meant for the condition of success
	# 	username_test = User.get_or_none(User.username == form.username.data)
	# 	email_test = User.get_or_none(User.email == form.email.data)
	# 	if username_test == None and email_test == None:
	# 		updated_user.save() # does this create new or update??
	# 		flash('Data saved', 'success')
	# 	else:
	# 		flash('Duplication of either username or email', 'warning')
"""
End of Update User
"""

@users_blueprint.route('/logout')
@login_required
def logout():
	logout_user()
	flash("You've been logged out!", "success")
	return redirect(url_for('users.index'))