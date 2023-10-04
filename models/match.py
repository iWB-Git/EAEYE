from mongoengine import *
from models.competition import Competition
from models.player import Stats, Goal


class MatchStats(EmbeddedDocument):
    match_id = ReferenceField('Match', dbref=False)
    player_id = ReferenceField('Player', dbref=False)
    starter = BooleanField(default=False)
    min_played = IntField(default=0)
    goals = EmbeddedDocumentListField(Goal, default=[])
    assists = IntField(default=0)
    yellow_cards = IntField(default=0)
    red_cards = IntField(default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.match_id = kwargs['match_id']
        self.player_id = kwargs['player_id']


class Match(DynamicDocument):
    competition_id = ReferenceField('Competition', dbref=False)
    home_team = ReferenceField('Team', dbref=False)
    away_team = ReferenceField('Team', dbref=False)
    date = StringField()
    venue = StringField(default=None)
    match_url = StringField(default=None)
    home_stats = EmbeddedDocumentListField(MatchStats, dbref=False, default=[])
    away_stats = EmbeddedDocumentListField(MatchStats, dbref=False, default=[])
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
