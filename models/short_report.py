from mongoengine import *
# player document
from models.player import Player
# match document
from models.match import Match


# list with strengths & weaknesses
class attribute_list(EmbeddedDocument):
    attribute = StringField(unique=True)


class short_report(DynamicDocument):
    report_id = ObjectIdField(primary_key=True)
    player_id = ReferenceField(Player)  # Reference to the Player model
    match_id = ReferenceField(Match)  # Reference to the Match model
    game_context = StringField()
    report_date = DateField()
    player_profile = StringField()
    scout_name = StringField()
    formation = StringField()
    position = StringField()
    physical_profile = StringField()
    summary = StringField()
    grade = StringField()
    action = StringField()
    time_ready = DateField()
    conclusion = StringField()
    strength = EmbeddedDocumentListField(attribute_list)
    weakness = EmbeddedDocumentListField(attribute_list)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        # self.game_context = values['game_context']
        # self.scout_name = values['scout_name']
        # self.formation = values['formation']
        # self.physical_profile = values['physical_profile']
        # self.conclusion = values['conclusion']
        # self.position = values['position']
        # self.summary = values['summary']
        # self.grade = values['grade']
