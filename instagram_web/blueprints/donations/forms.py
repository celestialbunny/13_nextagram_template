from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired

class CreateDonateForm(FlaskForm):
	amount = FileField(
		'Amount',
		validators=[
			DataRequired()
		]
	)
	card_number = StringField(
		'Card Number',
		validators=[
			DataRequired()
		]
	)
	expiry_date = DateField(
		'Expiry Date MM/YY',
		validators=[
			DataRequired()
		]
	)
	submit = SubmitField('Donate')