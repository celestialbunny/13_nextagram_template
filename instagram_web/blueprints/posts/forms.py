from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class CreatePostForm(FlaskForm):
	# image = FileField(
	# 	'Image',
	# 	validators=[
	# 		DataRequired()
	# 	]
	# )
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