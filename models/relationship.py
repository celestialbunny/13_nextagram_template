# from peewee import ForeignKeyField, Model
# from models.user import User

# class Relationship(Model):
# 	from_user = ForeignKeyField(User, backref="relationships")
# 	to_user = ForeignKeyField(User, backref="related_to")

# 	class Meta:
# 		indexes = (
# 			(('from_user', 'to_user'), True)
# 		)
# 	def __repr__(self):
# 		return f"('{self.from_user} is following '{self.to_user}')"