from flask import Blueprint, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from peewee import IntegrityError

# importing related to User & it's forms
from models.user import User
from instagram_web.blueprints.users.forms import RegistrationForm, LoginForm, UpdateDetailsForm

# Common import that shares with the posts.py
from flask import render_template, redirect, url_for, flash, request, session, escape
from flask_login import login_user, logout_user, login_required, current_user


users_blueprint = Blueprint('users',
							__name__,
							template_folder='templates/users')

def redirect_if_logged_in():
	if current_user.is_authenticated:
		flash("You have already been logged in", "warning")
		return redirect(url_for('users.index'))

@users_blueprint.route('/', methods=["GET"])
def index():
	return render_template('index.html')

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
		user = User.get_or_none(User.email == form.email.data)
		password = check_password_hash(user.password, form.password.data)
		if user and password:
			login_user(user)
			flash("You've been logged in!", "success")
			if next_page:
				return redirect(url_for(next_page))
			else:
				return redirect(url_for('users.index'))
		else:
			flash("Login unsuccessful, Please check email and password", "danger")
"""
End of Login User
"""

@users_blueprint.route('/logout')
@login_required
def logout():
	logout_user()
	flash("You've been logged out!", "success")
	return redirect(url_for('users.index'))