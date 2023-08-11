from mongoengine import *
from bson.objectid import ObjectId


class Goal(EmbeddedDocument):
    minute = IntField(default=None)
    match_id = ReferenceField('Match', dbref=False)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.minute = values['minute']


class PlayerTeam(EmbeddedDocument):
    team_id = ReferenceField('Team', dbref=False)
    reg_date = StringField(default=None)
    on_team = BooleanField(default=True)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.team_id = values['team_id']
        self.reg_date = values['reg_date']
        self.on_team = values['on_team']


class Stats(EmbeddedDocument):
    match_day_squad = IntField(default=0)
    starter = IntField(default=0)
    min_played = IntField(default=0)
    starter_minutes = IntField(default=0)
    sub_minutes = IntField(default=0)
    goals = EmbeddedDocumentListField(Goal, default=[])
    assists = IntField(default=0)
    yellow_cards = IntField(default=0)
    red_cards = IntField(default=0)
    clean_sheets = IntField(default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Player(DynamicDocument):
    name = StringField(required=True)
    first_name = StringField()
    last_name = StringField()
    dob = StringField()
    nationality = StringField(default='none')
    jersey_num = IntField(default=0)
    stats = EmbeddedDocumentField(Stats)
    teams = EmbeddedDocumentListField(PlayerTeam, default=[])
    matches = ListField(ReferenceField('Match'))

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.name = values['name']
        # self.first_name = self.name.split()[0]
        # self.last_name = self.name.split()[1]
        self.dob = values['dob']
        self.nationality = values['nationality']
        self.jersey_num = values['jersey_num']
        self.stats = Stats().to_mongo()
