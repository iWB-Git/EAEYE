from mongoengine import *


class Match(Document):
    competition = StringField(required=True)
    year = StringField()
    round = StringField()
    fixture = StringField()
    competition_id = ReferenceField('Competition', dbref=False)
    teams_id = ListField(ReferenceField('Team', dbref=False))

    def __init__(self, comp_name, year, round, fixture, *args, **values):
        super().__init__(*args, **values)
        self.competition = comp_name
        self.year = year
        self.round = round
        self.fixture = fixture
        self.teams_id = []