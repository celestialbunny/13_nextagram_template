from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class CreatePostForm(FlaskForm):
	picture = FileField(
		'Picture',
		validators=[
			DataRequired(),
			FileAllowed(['jpg', 'png'])
		]
	)
	title = StringField(
		'Title',
		validators=[
			DataRequired()
		]
	)
	content = TextAreaField(
		'Content'
	)
	submit = SubmitField('Post')