from mongoengine import *
from models.competition import Competition


class Country(Document):
    name = StringField(required=True)
    competitions = ListField(ReferenceField('Competition', dbref=False), default=[])

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.name = values['name']
