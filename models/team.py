from mongoengine import *


class Team(Document):
    name = StringField(required=True)
    roster = ListField(ReferenceField('Player', dbref=True, default=[]))
    matches = ListField(ReferenceField('Match', dbref=True, default=[]))

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.name = values['name']
        self.roster = values['roster']
        self.matches = values['matches']
