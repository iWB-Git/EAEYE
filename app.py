import copy
import traceback
import urllib

import bson
from flask import Flask, request  # , jsonify, stream_with_context, render_template
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bson.json_util as json_util
import json
# import data_parse_methods
import match_data_upload
from html_responses import *
from logging.config import dictConfig
from models.player import Player, PlayerTeam, Stats, Goal
from models.match import Match
from models.fixture import Fixture, Round
from models.team import Team
import os
import mongoengine
from datetime import datetime
# from test_json import TEST_JSON_NEW as test_match_data
# import json
# from templates import Player
# import yaml
from bson.objectid import ObjectId
# from requests_html import HTMLSession
# import requests
# from csv_parse import read_csv

TEST_JSON_FIXTURE = {"competition_name":"Ligi Kuu Tanzania Bara","competition_year":"2023/24","rounds":"4","round_data":[{"round":1,"round_data":[{"MatchUp":1,"Date":"2023-08-08","HomeTeam":"Young Africans Sports Club","AwayTeam":"Singida BS","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":2,"Date":"2023-08-23","HomeTeam":"Young Africans Sports Club","AwayTeam":"Ihefu Sports Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":3,"Date":"2023-08-17","HomeTeam":"Azam Football Club","AwayTeam":"Mtibwa Sugar Sports Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":4,"Date":"2023-08-17","HomeTeam":"Young Africans Sports Club","AwayTeam":"Mtibwa Sugar Sports Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"}]},{"round":2,"round_data":[{"MatchUp":1,"Date":"2023-08-04","HomeTeam":"Young Africans Sports Club","AwayTeam":"Azam Football Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":2,"Date":"2023-08-11","HomeTeam":"Young Africans Sports Club","AwayTeam":"Ihefu Sports Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":3,"Date":"2023-08-18","HomeTeam":"Geita Gold FC","AwayTeam":"Fountain Gate Princess","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":4,"Date":"2023-08-18","HomeTeam":"Mtibwa Sugar Sports Club","AwayTeam":"Singida BS","FullMatchURL":"-","Venue":"Bukhungu Stadium"}]},{"round":3,"round_data":[{"MatchUp":1,"Date":"2023-08-09","HomeTeam":"KMC FC","AwayTeam":"Geita Gold FC","FullMatchURL":"https://www.youtube.com","Venue":"-"},{"MatchUp":2,"Date":"2023-08-03","HomeTeam":"Namungo FC","AwayTeam":"Namungo FC","FullMatchURL":"https://www.youtube.com","Venue":"-"},{"MatchUp":3,"Date":"2023-08-18","HomeTeam":"Ihefu Sports Club","AwayTeam":"Coastal Union SC","FullMatchURL":"https://www.youtube.com","Venue":"-"},{"MatchUp":4,"Date":"2023-08-25","HomeTeam":"Singida BS","AwayTeam":"Fountain Gate Princess","FullMatchURL":"-","Venue":"-"}]}]}

# rudimentary dev testing access codes
DIRECT_USERNAME = os.environ['URL_DIRECT_USERNAME']
DIRECT_PASSWORD = os.environ['URL_DIRECT_PASSWORD']
TONY_USERNAME = os.environ['TONY_DIRECT_USERNAME']

# flask logging setup, may not end up being used
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# main application setup
app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {'DB': 'ea_eye'}
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# MongoDB setup and initialization
db_username = urllib.parse.quote_plus(os.environ['DB_USERNAME'])
db_password = urllib.parse.quote_plus(os.environ['DB_PASSWORD'])
db_uri = os.environ['DB_URI'] % (db_username, db_password)
db = mongoengine.connect(alias='default', host=db_uri)
db = db.ea_eye


def append_data(data, html_response):
    to_bytes = json_util.dumps(data)
    response = copy.deepcopy(html_response)
    response[0]['data'] = to_bytes
    return response


def edit_html_desc(html_response, new_desc):
    new_response = copy.deepcopy(html_response)
    new_response[0]['Description'] = new_desc
    return new_response


# brief landing page if someone somehow ends up on the API's home page
@app.route('/')
def index():
    return '<h1>EA Eye API</h1>' \
           '<p>Please contact administrator for access</p>'


# endpoint for devs to quickly clear a MongoDB collection
# <collection>: collection to clear
# <username>: dev's provided username
# <password>: dev's provided password
@app.route('/api/v1/clear-collection/<collection>/<username>/<password>/CONFIRM/YES', methods=['DELETE'])
def clear_db_docs(collection, username, password):
    # check if credentials match a developer's credentials
    # if yes: clear <collection>
    # else: return 404 PAGE NOT FOUND error to conceal endpoint
    if (username == DIRECT_USERNAME or username == TONY_USERNAME) and password == DIRECT_PASSWORD:
        db[collection].delete_many({})
        return SUCCESS_200
    else:
        return ERROR_404


# endpoint to upload match data
# verifies the data's formatting then parses and uploads to MongoDB
# <data>: the data to be uploaded in JSON format
@app.route('/api/v1/upload-match-data/', methods=['POST'])
def upload_match_data():
    # try to load in <data>
    # if successful: parse data and upload to MongoDB
    # else: return 400 BAD REQUEST error
    return edit_html_desc(ERROR_404, 'Outdated endpoint. Please use \'/api/v2/upload-match-data\' to upload player '
                                     'match data')
    # try:
    #     data = json.loads(request.data)
    #     match_data_upload.split_match_data(data)
    #     return SUCCESS_201
    # except Exception as e:
    #     print('ERROR LOADING MATCH DATA: ' + str(e))
    #     return ERROR_400


def update_player_stats(team, match_id):
    stats_list = []
    for squad in team:
        for player in team[squad]:
            player_id = ObjectId(player['PlayerID'])
            db_player = db.players.find_one({'_id': player_id})
            if db_player:
                if match_id in db_player['matches']:
                    continue
                player_stats = db_player['stats']
                player_stats['match_day_squad'] += 1
                min_played = 0
                if player['starter'] == 'YES':
                    player_stats['starter'] += 1
                    min_played = 90 if player['SubOut'] == 'NO' else 90 - int(player['SubMinute'])
                    player_stats['starter_minutes'] += min_played
                elif player['substitute'] == 'YES':
                    min_played = 90 - int(player['SubMinute']) if player['SubIn'] == 'YES' else 0
                    player_stats['sub_minutes'] += min_played
                player_stats['min_played'] += min_played
                if player['Goal']:
                    goal_mins = player['GoalMinute'].split(',')
                    for i in range(0, player['Goal']):
                        player_stats['goals'].append(Goal(minute=goal_mins[i], match_id=match_id).to_mongo())
                db.players.update_one({'_id': player_id},
                                      {'$set': {'stats': player_stats},
                                       '$addToSet': {'matches': match_id}})
                stats_list.append(player_stats)
    return stats_list


@app.route('/api/v2/upload-match-data', methods=['POST'])
def upload_match_data_v2():
    try:
        data = json.loads(request.data)
        # data = test_match_data
        match_id = ObjectId(data['Competition']['MatchID'])
        home_id = ObjectId(data['HomeTeam']['teamID'])
        away_id = ObjectId(data['AwayTeam']['teamID'])

        db.teams.update_one({'_id': home_id}, {'$addToSet': {'matches': match_id}})
        db.teams.update_one({'_id': away_id}, {'$addToSet': {'matches': match_id}})

        home_stats = update_player_stats(data['HomeTeam']['Players'], match_id)
        away_stats = update_player_stats(data['AwayTeam']['Players'], match_id)

        db.matches.update_one({'_id': match_id},
                              {'$set': {
                                  'data_entered': True,
                                  'home_stats': home_stats,
                                  'away_stats': away_stats
                              }})

        return SUCCESS_200
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/get-collection/<collection>', methods=['GET'])
def get_collection(collection):
    if collection not in db.list_collection_names():
        return edit_html_desc(ERROR_404, 'Specified collection does not exist.')
    docs = list(db[collection].find({}))
    return append_data(docs, SUCCESS_200)


@app.route('/api/v1/get-document/<collection>/<_id>', methods=['GET'])
def get_document(collection, _id):
    try:
        doc = db[collection].find_one({'_id': ObjectId(_id)})
        return append_data(doc, SUCCESS_200) if doc else ERROR_404
    except Exception as e:
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/get-document/<collection>/name/<name>', methods=['GET'])
def get_document_by_name(collection, name):
    # doc = db[collection].find({'name': {'$regex': '/^name$/i'}})
    doc = db[collection].find_one({'name': name})
    return append_data(doc, SUCCESS_200) if doc else ERROR_404


@app.route('/api/v1/get-match-entries/<collection>', methods=['GET'])
def get_match_entries(collection):
    pass


# endpoint to retrieve all documents in the players collection
@app.route('/api/v1/get-player-data/all', methods=['GET'])
def get_all_player_data():
    # get list of all players in player collection and format into bytes for JSON response
    # docs = list(db.players.find({}, {'_id': 0}))
    # return append_data(docs, SUCCESS_200)
    return edit_html_desc(ERROR_404, 'Outdated endpoint. Please use \'/api/v1/get-collection/<collection>\' to access '
                                     'all data from a given collection.')


@app.route('/api/v1/get-roster/<team_id>', methods=['GET'])
def get_roster(team_id):
    try:
        team = db.teams.find_one({'_id': ObjectId(team_id)})
        if not team:
            return edit_html_desc(ERROR_404, 'ID not found in teams collection. Check your OID and try again.')
        roster = team['roster']
        ids = []
        for _id in roster:
            if type(_id) is ObjectId:
                ids.append(_id)
            else:
                ids.append(ObjectId(_id['$oid']))
        players = list(db.players.find({'_id': {'$in': ids}}))
        return append_data(players, SUCCESS_200)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/insert-player/', methods=['POST'])
def insert_player():
    try:
        player_data = json.loads(request.data)
        # player_data = TEST_JSON_PLAYER

        name = player_data['names'].strip()
        nationality = player_data['nationality']
        dob = player_data['dob']
        position = player_data['position']
        jersey_num = player_data['jersey_num']
        supporting_file = player_data['supporting_file']
        reg_date = player_data['reg_date']

        db_team = db.teams.find_one({'_id': ObjectId(player_data['team_id'])})

        new_player = Player(name=name, dob=dob, nationality=nationality, jersey_num=jersey_num, supporting_file=supporting_file, position=position)
        player_club = PlayerTeam(team_id=db_team['_id'], reg_date=reg_date, on_team=True)

        new_player['teams'].append(player_club.to_mongo())
        # new_player['supporting_file'] = supporting_file

        db_player = db.players.insert_one(new_player.to_mongo())
        db.teams.update_one({'_id': db_team['_id']}, {'$addToSet': {'roster': db_player.inserted_id}})

        return SUCCESS_201
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/move-player', methods=['POST'])
def move_player():
    try:
        data = json.loads(request.data)
        player_id = ObjectId(data['player_id'])
        old_team_id = ObjectId(data['old_team_id'])
        new_team_id = ObjectId(data['new_team_id'])
        reg_date = data['reg_date']
        db_player = db.players.find_one({'_id': player_id})
        if not db_player:
            return edit_html_desc(ERROR_404, 'ID not found in players collection. Check your OID and try again.')
        for team in db_player['teams']:
            if type(team['team_id']) is ObjectId:
                if team['team_id'] == old_team_id:
                    team['on_team'] = False
            elif ObjectId(team['team_id']['$oid']) == old_team_id:
                team['on_team'] = False
        new_team = PlayerTeam(team_id=new_team_id, reg_date=reg_date, on_team=True)
        db.players.update_one({'_id': player_id}, {'$addToSet': {'teams': new_team.to_mongo()}})
        db.teams.update_one({'_id': new_team_id}, {'$addToSet': {'roster': player_id}})
        db.teams.update_one({'_id': old_team_id}, {'$pull': {'roster': {'_id': player_id}}})
        return append_data(db.players.find_one({'_id': player_id}), SUCCESS_200)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/update-one/<collection>', methods=['POST'])
def update_document(collection):
    try:
        new_doc = json.loads(request.data)
        _id = new_doc['_id']['$oid']
        db_doc = db[collection].find_one({'_id': ObjectId(_id)})
        if not db_doc:
            return edit_html_desc(ERROR_404, 'ID not found in players collection. Check your OID and try again.')
        new_values = {}
        for key in new_doc:
            if key == '_id':
                continue
            if not new_doc[key] == db_doc[key]:
                new_values[key] = new_doc[key]
        # update_result = db[collection].update_one({'_id': ObjectId(_id)}, {'$set': new_values})
        updated_doc = db[collection].find_one({'_id': ObjectId(_id)})
        return append_data(updated_doc, SUCCESS_200)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/get-teams/<comp_id>', methods=['GET'])
def get_teams_from_comp(comp_id):
    try:
        competition = db.competitions.find_one({'_id': ObjectId(comp_id)})
        if not competition:
            return edit_html_desc(ERROR_404, 'ID not found in competitions collection. Check your OID and try again.')
        team_ids = competition['teams']
        teams = db.teams.find({'_id': {'$in': team_ids}})
        return append_data(teams, SUCCESS_200)
    except Exception as e:
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/upload-fixture-data/', methods=['POST'])
def upload_fixture_data():
    try:
        data = json.loads(request.data)
        comp_name = data['competition_name']
        db_comp = db.competitions.find_one({'name': comp_name})
        comp_id = db_comp['_id']
        comp_year = data['competition_year']
        rounds_list = data['round_data']
        new_fixture = Fixture(competition=comp_id, comp_year=comp_year, rounds=[])
        for round in rounds_list:
            match_ids = []
            for matchup in round['round_data']:
                home_team = matchup['HomeTeam']
                away_team = matchup['AwayTeam']
                home_id = db.teams.find_one({'name': home_team})['_id']
                away_id = db.teams.find_one({'name': away_team})['_id']
                date = matchup['Date']
                match_url = matchup['FullMatchURL']
                venue = matchup['Venue']
                new_match = Match(competition_id=comp_id, home_team=home_id, away_team=away_id, date=date, venue=venue, match_url=match_url)
                match_ids.append(db.matches.insert_one(new_match.to_mongo()).inserted_id)
            new_round = Round(matchups=match_ids)
            new_fixture['rounds'].append(new_round.to_mongo())
        db.fixtures.insert_one(new_fixture.to_mongo())
        return SUCCESS_201
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))

# USED TO UPDATE PLAYER DB TO ENSURE ALL HAVE 'supporting_file' KEY/VAL PAIR
# NO LONGER NEEDED BUT LEAVING IN PLACE FOR NOW
# def add_supporting_file_key():
#     try:
#         players = list(db.players.find({}))
#         counter = 0
#         for player in players:
#             if 'supporting_file' in player:
#                 continue
#             db.players.update_one({'_id': player['_id']}, {'$set': {'supporting_file': ''}})
#             print(counter + 1)
#             counter += 1
#     except Exception as e:
#         traceback.print_exception(type(e), e, e.__traceback__)


if __name__ == '__main__':
    # insert_player()
    # upload_match_data_v2()
    # upload_fixture_data(TEST_JSON_FIXTURE)
    # add_supporting_file_key()
    # test_match = Match(competition_id=ObjectId('64d52c9f4cdabb9dfc3b4a53'), home_team=ObjectId('64d52c9f4cdabb9dfc3b4a6a'), away_team=ObjectId('64d52c9f4cdabb9dfc3b4a83'), date='testDate', venue='testVen', match_url='testURL')
    # print(test_match.to_mongo().to_dict())
    app.debug = False
    app.run()
