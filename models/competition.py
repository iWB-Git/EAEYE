from mongoengine import *


class Competition(Document):
    name = StringField(required=True)
    teams = ListField(ReferenceField('Team', dbref=True, default=[]))
    body_id = ReferenceField('Body', dbref=False, default=None)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.name = values['name']
        self.teams = values['teams']
        self.body_id = values['body_id']
