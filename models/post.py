from models.base_model import BaseModel
from peewee import CharField, IntegerField, TextField

class Post(BaseModel):
	title = CharField(unique=False, null=False)
	content = TextField(unique=False, null=False)
	status = IntegerField(unique=False, null=True)

	def __repr__(self):
		return f"Post('{self.title}, '{self.content}')"