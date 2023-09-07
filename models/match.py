from mongoengine import *
from models.competition import Competition
from models.player import Stats, Goal


class Match(DynamicDocument):
    competition_id = ReferenceField('Competition', dbref=False)
    home_team = ReferenceField('Team', dbref=False)
    away_team = ReferenceField('Team', dbref=False)
    date = StringField()
    venue = StringField(default=None)
    match_url = StringField(default=None)
    home_stats = EmbeddedDocumentListField(Stats, dbref=False, default=[])
    away_stats = EmbeddedDocumentListField(Stats, dbref=False, default=[])
    data_entered = BooleanField(default=False)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.competition_id = values['competition_id']
        self.home_team = values['home_team']
        self.away_team = values['away_team']
        self.date = values['date']
        self.venue = values['venue']
        self.match_url = values['match_url']
        # self.home_stats = []
        # self.away_stats = []
        # self.data_entered = False
