from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.post import Post
from peewee import DecimalField, ForeignKeyField

class Donation(BaseModel):
	donor_id = ForeignKeyField(User, backref='donor')
	recipient_id = ForeignKeyField(User, backref='recipient')
	post_id = ForeignKeyField(Post, backref='donated_post')
	amount = DecimalField(unique=False, null=False)

	def __repr__(self):
		return f"Donation('{self.donor_id}', '{self.recipient_id}', '{self.post_id}', {self.amount})"