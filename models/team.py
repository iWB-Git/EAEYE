from mongoengine import *
from bson.objectid import ObjectId


class Team(Document):
    name = StringField(required=True)
    roster = ListField(ReferenceField('Player'), dbref=True, default=[])

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.name = values['name']
        self.roster = values['roster']

    def to_dict(self):
        return {'name': self.name, 'roster': self.roster}
