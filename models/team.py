from mongoengine import *
from bson.objectid import ObjectId


class Team(Document):
    name = StringField(required=True)
    roster = ListField(ReferenceField('Player'), dbref=True)

    def __init__(self, name, *args, **values):
        super().__init__(*args, **values)
        self.name = name

    def to_dict(self):
        return {'name': self.name, 'roster': self.roster}
