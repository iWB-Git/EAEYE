from mongoengine import *
from models.competition import Competition


class Match(DynamicDocument):
    # competition = StringField(required=True)
    # year = StringField()
    date = StringField()
    # round = StringField()
    # fixture = StringField()
    competition_id = ReferenceField('Competition', dbref=False)
    match_url = StringField(default=None)
    # teams_id = ListField(ReferenceField('Team', dbref=False))
    home_team = ReferenceField('Team', dbref=False)
    away_team = ReferenceField('Team', dbref=False)
    venue = StringField(default=None)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        # self.competition = values['comp_name']
        # self.year = year
        self.date = values['date']
        self.venue = values['venue']
        self.match_url = values['match_url']
        # self.round = values['round']
        self.competition_id = values['comp_id']
        # self.fixture = values['fixture']
        # self.teams_id = []
        self.home_team = values['home_team']
        self.away_team = values['away_team']

