from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
	username = StringField(
		'Username',
		validators=[
			DataRequired(),
			Length(min=5, max=20)
		]
	)
	email = StringField(
		'Email',
		validators=[
			DataRequired(),
			Email()
		]
	)
	password = PasswordField(
		'Password',
		validators=[
			DataRequired(),
			Length(min=8, max=20)
		]
	)
	btn = SubmitField('Sign Up')


class LoginForm(FlaskForm):
	email = StringField(
		'Email',
		validators=[
			DataRequired(),
			Email()
		]
	)
	password = PasswordField(
		'Password',
		validators=[
			DataRequired()
		]
	)
	# remember = BooleanField('Remember Me')
	btn = SubmitField('Login')

class UpdateDetailsForm(FlaskForm):
	username = StringField(
		'Username',
		validators=[
			DataRequired(),
			Length(min=5, max=20)
		]
	)
	email = StringField(
		'Email',
		validators=[
			DataRequired(),
			Email()
		]
	)
	password = PasswordField(
		'Password',
		validators=[
			DataRequired(),
			Length(min=8, max=20)
		]
	)
	picture = FileField(
		'Update Profile Picture',
		validators=[
			FileAllowed(['jpg', 'png'])
		]
	)
	submit = SubmitField('Update Profile')