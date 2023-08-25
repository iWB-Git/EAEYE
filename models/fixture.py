from mongoengine import *
from models.match import Match


class Round(EmbeddedDocument):
    matchups = ListField(ReferenceField('Match'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matchups = kwargs['matchups']


class Fixture(Document):
    competition = ReferenceField('Competition')
    comp_year = StringField(default=None)
    rounds = EmbeddedDocumentListField('Round', default=[])

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.competition = values['competition']
        self.comp_year = values['comp_year']
        self.rounds = values['rounds']
