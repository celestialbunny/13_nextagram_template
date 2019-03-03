from models.base_model import BaseModel
from peewee import ForeignKeyField, Model, CharField, IntegrityError, BooleanField
import datetime
from flask_login import UserMixin

class User(UserMixin, BaseModel):
	username = CharField(unique=True, null=False)
	email = CharField(unique=True, null=False)
	password = CharField(unique=True, null=False)
	image_file = CharField(unique=False, null=True, default='https://celestialbunny-nextagram.s3.amazonaws.com/default.png')
	is_public = BooleanField(unique=False, null=False, default=True)

	def validate_username(self, username):
		user = User.get_or_none(User.username == username)
		if user:
			raise IntegrityError('Username has already been taken')

	def validate_email(self, email):
		user = User.get_or_none(User.email == email)
		if user:
			raise IntegrityError('Email address has already been taken')

	# This is applicable for Users that are not "private"
	# def following(self):
	# 	"""The users that the user is following"""
	# 	return (
	# 		User.select().join(
	# 			Relationship, on=Relationship.to_user
	# 		).where(
	# 			Relationship.from_user == self
	# 		)
	# 	)

	# This is applicable for Users that are not "private"
	# def followers(self):
	# 	"""Get users following the current user"""
	# 	return(
	# 		User.select().join(
	# 			Relationship, on=Relationship.from_user
	# 		).where(
	# 			Relationship.to_user == self
	# 		)
	# 	)

	def following(self):
		"""The users that the user is following with approval 'True'"""
		return (
			User.select().join(
				Relationship, on=Relationship.to_user
			).where(
				# Relationship.from_user == self and
				Relationship.approval == True
			)
		)

	def followers(self):
		"""Get users following the current user"""
		return(
			User.select().join(
				Relationship, on=Relationship.from_user
			).where(
				Relationship.approval == True
			)
		)

	def __repr__(self):
		return f"Post('{self.username}, '{self.email}', '{self.image_file}', '{self.is_public}')"

class Relationship(Model):
	from_user = ForeignKeyField(User, backref="follower")
	to_user = ForeignKeyField(User, backref="followee")
	# approval = BooleanField(unique=False, null=False)
	approval = BooleanField(unique=False, null=False, default=False)

	def to_user_allow_follow(self):
		pass

	def __repr__(self):
		return f"('{self.from_user} is following '{self.to_user}')"