import json
from flask import request
import urllib
import os
import copy
from flask import jsonify
from htmlcodes import SUCCESS_200, SUCCESS_201, ERROR_400, ERROR_404, ERROR_405
import mongoengine
from models import short_report
from models.player import Player, PlayerTeam
from models.match import Match, MatchStats
from bson.objectid import ObjectId
import bson.json_util as json_util
import motor.motor_asyncio
from mongoengine.errors import DoesNotExist
from models.short_report import short_report

# MongoDB setup and initialization
db_username = urllib.parse.quote_plus(os.environ['DB_USERNAME'])
db_password = urllib.parse.quote_plus(os.environ['DB_PASSWORD'])
# db_uri = os.environ['DB_URI'] % (db_username, db_password)
db_uri = os.environ['DB_URI'].format(username=db_username, password=db_password)
db = mongoengine.connect(alias='default', host=db_uri)

# reference to ea_eye database
db = db.ea_eye
# reference to short_report collection in the ea_eye database
short_report_collection = db.short_report

client = motor.motor_asyncio.AsyncIOMotorClient(db_uri)
db_0 = client.ea_eye


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
    # update'data' field of copied html_response with JSON-formatted string (to_bytes).
    response[0]['data'] = to_bytes
    # returns modified html_response
    return response


# test
def hello():
    return SUCCESS_201


# fetching player details
def fetch_player_details(player_id):
    try:
        # Try to find player with the given ID
        player = db.players.find_one({'_id': player_id})

        # Extract relevant details from the player object
        player_details = {
            'player_name': player['name'],
            'date_of_birth': player['dob'],
            'shirt_number': player['jersey_num'],
            'position_played': player['position']
        }

        # Return the extracted details
        return player_details

    except DoesNotExist:
        # If player not found, return an error message
        return {'error': 'Player not found'}


# fetching match details
def fetch_match_details(match_id, player_team_id, player_id):
    try:
        # Try to find a match with the given ID
        match = db.matches.find_one({'_id': match_id})

        # Determine the opposition club based on the home and away teams
        opposition_club = match['away_team']['name'] if match['home_team']['id'] == player_team_id else \
            match['home_team']['name']

        # Calculate total minutes played in the match
        mins_played = 0  # initialize to 0
        for stats in (match['away_stats'] + match['home_stats']):
            if stats['player_id'] == player_team_id:
                mins_played = stats['min_played']

        game_date = match.date()

        # Return the extracted details
        return {
            'opposition_club': match['opposition_club'],
            'mins_played': match['mins_played'],
            'game_date': match['game_date']
        }

    except DoesNotExist:
        # If match not found, return an error message
        return {'error': 'Match not found'}


# creating shortreport POST method
def upload_short_report():
    try:
        # get JSON data from the request
        data = request.get_json()

        # Extract player_id and match_id from the request
        player_id = return_oid(data.get('player_id'))
        match_id = return_oid(data.get('match_id'))
        player_team_id = return_oid(data.get('player_team_id'))

        # Fetch player and match details
        player_details = fetch_player_details(player_id)
        match_details = fetch_match_details(match_id, player_team_id, player_id)

        if 'error' in player_details:
            return jsonify({'error': player_details['error']}), 404
        if 'error' in match_details:
            return jsonify({'error': match_details['error']}), 404

        # Combine all details with received scouting report data
        short_report_data = short_report(
            formation=data['formation'],
            position_played=data['positionPlayer'],
            report_date=data['reportDate'],
            scout_name=data['scoutName'],
            player_profile=data['playerProfile'],
            game_context=data['gameContext'],
            position=data['position_played'],
            physical_profile=data['physicalProfile'],
            summary=data['gameSummary'],
            conclusion=data['playerConclusion'],
            grade=data['grade'],
            action=data['nextAction'],
            time_ready=data['readyTimes'],
            strength={key: value for key, value in data.items() if key.startswith('strength')},
            weakness={key: value for key, value in data.items() if key.startswith('weakness')}
        )

        short_report_data['strengths'].append(['strength'].to_mongo())
        short_report_data['weaknesses'].append(['weakness'].to_mongo())

        # Save the scouting report to the database
        inserted_id = short_report.insert_one(short_report_data.to_mongo()).inserted_id

        return append_data(inserted_id, SUCCESS_201)

    except Exception as e:
        return jsonify({'error': str(e)}), 500