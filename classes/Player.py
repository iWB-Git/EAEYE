from mongoengine import *


class Player(DynamicDocument):
    name = StringField(required=True)
    first_name = StringField
    last_name = StringField
    age = IntField
    nationality = StringField
