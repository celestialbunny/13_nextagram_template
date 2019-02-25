from models.base_model import BaseModel
from models.post import Post
import peewee as pw
import datetime
from flask_login import UserMixin

class User(UserMixin, BaseModel):
	username = pw.CharField(unique=True, null=False)
	email = pw.CharField(unique=True, null=False)
	password = pw.CharField(unique=True, null=False)
	post = pw.ForeignKeyField(Post, backref='author', unique=False, null=True)
	image_file = pw.CharField(unique=False, null=True, default='default.jpg')

	def validate_username(self, username):
		user = User.get_or_none(User.username == username)
		if user:
			raise pw.IntegrityError('Username has already been taken')

	def validate_email(self, email):
		user = User.get_or_none(User.email == email)
		if user:
			raise pw.IntegrityError('Email address has already been taken')

	def __repr__(self):
		return f"Post('{self.username}, '{self.email}', '{self.image_file}')"