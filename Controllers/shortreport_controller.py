from flask import request
import copy
from flask import jsonify
from htmlcodes import *
from models import short_report
from bson.objectid import ObjectId
import bson.json_util as json_util
from models.short_report import short_report
# from Controllers.player_controller import fetch_player_details
# from Controllers.match_controller import fetch_match_details
from Controllers import player_controller, match_controller
from models.short_report import attribute_list
import functions as fc
# from Controllers.player_controller import add_report_to_player


class ShortReportController:
    def __init__(self, db):
        self.db = db
        self.MC=match_controller.MatchController(db)
        self.PC = player_controller.PlayerController(db)

    # function takes an _id as input
    def return_oid(_id):
        # checks if  _id is already ObjectId If it is, it returns _id as is.
        # if type is not ObjectId, it converts _id to ObjectId using ObjectId(_id) and returns result.
        return _id if type(_id) is ObjectId else ObjectId(_id)

    # function takes two parameters: data and html_response
    def append_data(data, html_response):
        # use json_util.dumps(data) to convert data into a JSON-formatted string,then assigns result to to_bytes
        to_bytes = json_util.dumps(data)
        # create deep copy of html_response using copy.deepcopy(html_response)
        response = copy.deepcopy(html_response)
        # update 'data' field of copied html_response with JSON-formatted string (to_bytes).
        response[0]['data'] = to_bytes
        # returns modified html_response
        return response

    # creating shortreport POST method
    def upload_short_report(self):
        # try:
        # get JSON data from the request
        data = request.get_json()

        # Extract player_id and match_id from the request
        player_id = fc.return_oid(data['player_id'])
        match_id = fc.return_oid(data['match_id'])
        player_team_id = fc.return_oid(data['player_team_id'])

        # Fetch player and match details
        player = self.PC.fetch_player_details(player_id)
        player_details = {
            'player_name': player['name'],
            'date_of_birth': player['dob'],
            'shirt_number': player['jersey_num'],
            # 'position_played': player['position'],

        }

        match = self.MC.fetch_match_details(match_id)

        # Determine the opposition club based on the home and away teams
        opposition_club = match['away_team'] if match['home_team'] == player_team_id else \
            match['home_team']
        # Calculate total minutes played in the match
        mins_played = 0  # initialize to 0
        for stats in (match['away_stats'] + match['home_stats']):
            if stats['player_id'] == player_team_id:
                mins_played = stats['min_played']

        game_date = match['date']

        match_details = {
            'opposition_club': opposition_club,
            'mins_played': mins_played,
            'game_date': game_date,
        }
        # Return the extracted details

        if 'error' in player_details:
            return jsonify({'error': player_details['error']}), 404
        if 'error' in match_details:
            return jsonify({'error': match_details['error']}), 404

        # Combine all details with received scouting report data
        strengths_data = {key: value for key, value in data.items() if key.startswith('strength')}
        weaknesses_data = {key: value for key, value in data.items() if key.startswith('weakness')}

        strengths = [attribute_list(attribute=value) for value in strengths_data.values()]
        weaknesses = [attribute_list(attribute=value) for value in weaknesses_data.values()]

        short_report_data = short_report(
            player_id=data['player_id'],
            match_id=data['match_id'],
            formation=data['formation'],
            position_played=data['positionPlayed'],
            report_date=data['reportDate'],
            scout_name=data['scoutName'],
            player_profile=data['playerProfile'],
            game_context=data['gameContext'],
            position=data['position'],
            physical_profile=data['physicalProfile'],
            summary=data['gameSummary'],
            conclusion=data['playerConclusion'],
            grade=data['grade'],
            action=data['nextAction'],
            time_ready=data['readyTimes'],
            strengths=strengths,
            weaknesses=weaknesses
        )
        print(short_report_data.to_mongo())

        # Save the scouting report to the database
        inserted_id = self.db.short_reports.insert_one(short_report_data.to_mongo())

        inserted_id = inserted_id.inserted_id
        # self.PC.add_report_to_player(player_id=player_id, report_id=inserted_id)

        return SUCCESS_201
    #
    # except Exception as e:
    #
    #     return jsonify({'error': str(e)})
