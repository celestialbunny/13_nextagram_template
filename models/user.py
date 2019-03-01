from models.base_model import BaseModel
import peewee as pw
from peewee import ForeignKeyField, Model
import datetime
from flask_login import UserMixin

class User(UserMixin, BaseModel):
	username = pw.CharField(unique=True, null=False)
	email = pw.CharField(unique=True, null=False)
	password = pw.CharField(unique=True, null=False)
	image_file = pw.CharField(unique=False, null=True, default='https://celestialbunny-nextagram.s3.amazonaws.com/default.png')

	def validate_username(self, username):
		user = User.get_or_none(User.username == username)
		if user:
			raise pw.IntegrityError('Username has already been taken')

	def validate_email(self, email):
		user = User.get_or_none(User.email == email)
		if user:
			raise pw.IntegrityError('Email address has already been taken')

	def following(self):
		"""The users that the user is following"""
		return (
			User.select().join(
				Relationship, on=Relationship.to_user
			).where(
				Relationship.from_user == self
			)
		)

	def followers(self):
		"""Get users following the current user"""
		return(
			User.select().join(
				Relationship, on=Relationship.from_user
			).where(
				Relationship.to_user == self
			)
		)

	"""
	In order to get the posts not from yourself but from others
	refer to

	def get_num_followers
	runs a query whether this user exists
		true:
		false:

	OR

	create a list to run through
	"""

	def __repr__(self):
		return f"Post('{self.username}, '{self.email}', '{self.image_file}')"

class Relationship(BaseModel):
	from_user = ForeignKeyField(User, backref="follower")
	to_user = ForeignKeyField(User, backref="followee")

	def __repr__(self):
		return f"('{self.from_user} is following '{self.to_user}')"