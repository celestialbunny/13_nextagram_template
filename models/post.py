from models.base_model import BaseModel
from models.user import User
from peewee import CharField, IntegerField, TextField, ForeignKeyField

class Post(BaseModel):
	user = ForeignKeyField(User, backref='author')
	title = CharField(unique=False, null=False)
	content = TextField(unique=False, null=False)
	status = IntegerField(unique=False, null=True)

	def __repr__(self):
		return f"Post('{self.title}, '{self.content}')"