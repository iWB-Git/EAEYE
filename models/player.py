from mongoengine import *
from bson.objectid import ObjectId


class Goal(EmbeddedDocument):
    minute = IntField(default=None)
    match_id = ReferenceField('Match', dbref=False)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.minute = values['minute']


class Stats(EmbeddedDocument):
    match_day_squad = IntField(default=0)
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


class Player(Document):
    name = StringField(required=True)
    first_name = StringField()
    last_name = StringField()
    birth_year = IntField(default=2000)
    nationality = StringField(default='none')
    jersey_num = IntField(default=0)
    stats = EmbeddedDocumentField(Stats)
    teams_id = ListField(ReferenceField('Team', dbref=False))
    matches = ListField(ReferenceField('Match'))

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.name = values['name']
        self.first_name = self.name.split()[0]
        self.last_name = self.name.split()[1]
        self.birth_year = values['birth_year']
        self.nationality = values['nationality']
        self.jersey_num = values['jersey_num']
        self.stats = Stats().to_mongo()
