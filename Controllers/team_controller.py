import json
from urllib import request

import functions as fc
from htmlcodes import *
from models.team import *


class TeamController:
    def __init__(self, db):
        self.db = db

    def create_team(self, request_data):
        try:
            data = json.loads(request_data)
            comp_id = fc.return_oid(data['competition_id'])
            self.db.teams.insert_one(
                Team(
                    name=data['name'].strip().title(),
                    roster=[],
                    matches=[],
                    comps=[comp_id]
                ).to_mongo()
            )
            return SUCCESS_201
        except Exception as e:
            fc.print_and_return_error(e)

    def update_team_name(self,request_data):
        try:
            data = json.loads(request_data)
            team_id = fc.return_oid(data['teamId'])
            self.db.teams.update_one({'_id': team_id}, {'$set': {'name': data['name'].strip().title()}})
            return fc.edit_html_desc(SUCCESS_200, self.db.teams.find_one({'_id': team_id}))
        except Exception as e:
            fc.print_and_return_error(e)

