from mongoengine import *


class Competition(Document):
    name = StringField(required=True)
