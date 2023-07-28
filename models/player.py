from mongoengine import *
from bson.objectid import ObjectId


class Stats(EmbeddedDocument):
    goals = IntField(default=0)
    assists = IntField(default=0)
    min_played = IntField(default=0)
    yellow_cards = IntField(default=0)
    red_cards = IntField(default=0)
    clean_sheets = IntField(default=0)

    def to_dict(self):
        return {
            'goals': self.goals,
            'assists': self.assists,
            'min_played': self.min_played,
            'yellow_cars': self.yellow_cards,
            'red_cards': self.red_cards,
            'clean_sheets': self.clean_sheets
        }


class Player(Document):
    name = StringField(required=True)
    first_name = StringField()
    last_name = StringField()
    age = IntField(default=0)
    nationality = StringField(default='none')
    jersey_num = IntField(default=0)
    # stats = EmbeddedDocumentField(Stats)
    stats = {
        'goals': 0,
        'assists': 0,
        'min_played': 0,
        'yellow_cards': 0,
        'red_cards': 0,
        'clean_sheets': 0
    }
    teams_id = ListField(ReferenceField('Team', dbref=False))
    matches = ListField(ReferenceField('Match'))

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.name = values['name']
        self.age = values['age']
        self.nationality = values['nationality']
        self.jersey_num = values['jersey_num']
        # self.team = team
        # self.matches = matches

    def to_dict(self):
        return {
            'name': self.name,
            'age': self.age,
            'nationality': self.nationality,
            'jersey_num': self.jersey_num,
            'stats': self.stats,
            'teams_id': self.teams_id
        }
