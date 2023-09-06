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

TEST_JSON_LONG = {"Team_A":{"Name":"Team A","Players":{"Starters":[{"Name":"John Smith","SubOut":"YES","SubMinute":"34","Goal":3,"GoalMinute":"25,37,72","JerseyNumber":10,"checkId":"leftStarterCheck0","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Michael Johnson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":7,"checkId":"leftStarterCheck1","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Robert Davis","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":14,"checkId":"leftStarterCheck2","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"David Wilson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":5,"checkId":"leftStarterCheck3","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Daniel Thompson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":3,"checkId":"leftStarterCheck4","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Christopher Martinez","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":9,"checkId":"leftStarterCheck5","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Matthew Anderson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":23,"checkId":"leftStarterCheck6","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Andrew Taylor","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":16,"checkId":"leftStarterCheck7","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Joseph Clark","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":18,"checkId":"leftStarterCheck8","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"James Thomas","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":21,"checkId":"leftStarterCheck9","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Steven Walker","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":2,"checkId":"leftStarterCheck10","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"}],"Subbed":[{"Name":"Richard Rodriguez","SubIn":"YES","SubMinute":"34","Goal":0,"GoalMinute":"-","JerseyNumber":8,"checkId":"leftSubCheck11","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Paul Young","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":11,"checkId":"leftSubCheck12","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Mark Hall","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":6,"checkId":"leftSubCheck13","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Kevin Green","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":4,"checkId":"leftSubCheck14","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Anthony Harris","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":13,"checkId":"leftSubCheck15","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Charles White","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":17,"checkId":"leftSubCheck16","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Kenneth King","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":19,"checkId":"leftSubCheck17","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"George Lewis","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":20,"checkId":"leftSubCheck18","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Edward Turner","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":22,"checkId":"leftSubCheck19","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Thomas Hill","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":1,"checkId":"leftSubCheck20","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Brian Scott","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":15,"checkId":"leftSubCheck21","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"William Walker","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":12,"checkId":"leftSubCheck22","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"}]}},"Team_B":{"Name":"Team B","Players":{"Starters":[{"Name":"Daniel Brown","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":26,"checkId":"rightStarterCheck0","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Andrew Johnson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":27,"checkId":"rightStarterCheck1","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Christopher Davis","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":28,"checkId":"rightStarterCheck2","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Joseph Wilson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":29,"checkId":"rightStarterCheck3","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Michael Thompson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":30,"checkId":"rightStarterCheck4","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Matthew Thomas","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":31,"checkId":"rightStarterCheck5","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"John Martinez","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":32,"checkId":"rightStarterCheck6","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Robert Anderson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":33,"checkId":"rightStarterCheck7","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"James Clark","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":34,"checkId":"rightStarterCheck8","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"David Taylor","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":35,"checkId":"rightStarterCheck9","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Christopher Walker","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":36,"checkId":"rightStarterCheck10","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"}],"Subbed":[{"Name":"Steven Rodriguez","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":37,"checkId":"rightSubCheck11","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Richard Young","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":38,"checkId":"rightSubCheck12","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Mark Hall","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":39,"checkId":"rightSubCheck13","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Kevin Green","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":40,"checkId":"rightSubCheck14","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Anthony Harris","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":41,"checkId":"rightSubCheck15","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Charles White","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":42,"checkId":"rightSubCheck16","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Kenneth King","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":43,"checkId":"rightSubCheck17","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"George Lewis","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":44,"checkId":"rightSubCheck18","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Edward Turner","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":45,"checkId":"rightSubCheck19","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Thomas Hill","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":46,"checkId":"rightSubCheck20","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Brian Scott","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":47,"checkId":"rightSubCheck21","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"William Walker","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":48,"checkId":"rightSubCheck22","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"}]}},"Competition":{"Name":"FKF Premier League","Year":"2022/2023","Round":"Round 1","Fixture":"Gor Mahia vs AFC"}}

TEST_JSON = {"Team_A":{"Name": "Foxes", "Players":{"Starters":[{"Name": "Lightning Mcqueen", "SubOut": "NO", "SubMinute": "-", "Goal":0, "GoalMinute": ""}, {"Name": "David Degea", "SubOut": "NO", "SubMinute": "-", "Goal":0, "GoalMinute": ""}], "Subbed":[]}}, "Team_B":{"Name": "Lions", "Players":{"Starters":[{"Name": "Harry Maguire", "SubOut": "NO", "SubMinute": "-", "Goal":0, "GoalMinute": ""}, {"Name": "Bruno Fernandes", "SubOut": "YES", "SubMinute": "53", "Goal":0, "GoalMinute": ""}], "Subbed":[]}}, "Competition":{"Name": "Piston Cup", "Year": "2005", "Round": "2", "Fixture": "12"}}

TEST_JSON_FIXTURE = {"competition_name":"Ligi Kuu Tanzania Bara","competition_year":"2023/24","rounds":"4","round_data":[{"round":1,"round_data":[{"MatchUp":1,"Date":"2023-08-08","HomeTeam":"Young Africans Sports Club","AwayTeam":"Singida BS","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":2,"Date":"2023-08-23","HomeTeam":"Young Africans Sports Club","AwayTeam":"Ihefu Sports Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":3,"Date":"2023-08-17","HomeTeam":"Azam Football Club","AwayTeam":"Mtibwa Sugar Sports Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":4,"Date":"2023-08-17","HomeTeam":"Young Africans Sports Club","AwayTeam":"Mtibwa Sugar Sports Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"}]},{"round":2,"round_data":[{"MatchUp":1,"Date":"2023-08-04","HomeTeam":"Young Africans Sports Club","AwayTeam":"Azam Football Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":2,"Date":"2023-08-11","HomeTeam":"Young Africans Sports Club","AwayTeam":"Ihefu Sports Club","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":3,"Date":"2023-08-18","HomeTeam":"Geita Gold FC","AwayTeam":"Fountain Gate Princess","FullMatchURL":"https://www.youtube.com","Venue":"Bukhungu Stadium"},{"MatchUp":4,"Date":"2023-08-18","HomeTeam":"Mtibwa Sugar Sports Club","AwayTeam":"Singida BS","FullMatchURL":"-","Venue":"Bukhungu Stadium"}]},{"round":3,"round_data":[{"MatchUp":1,"Date":"2023-08-09","HomeTeam":"KMC FC","AwayTeam":"Geita Gold FC","FullMatchURL":"https://www.youtube.com","Venue":"-"},{"MatchUp":2,"Date":"2023-08-03","HomeTeam":"Namungo FC","AwayTeam":"Namungo FC","FullMatchURL":"https://www.youtube.com","Venue":"-"},{"MatchUp":3,"Date":"2023-08-18","HomeTeam":"Ihefu Sports Club","AwayTeam":"Coastal Union SC","FullMatchURL":"https://www.youtube.com","Venue":"-"},{"MatchUp":4,"Date":"2023-08-25","HomeTeam":"Singida BS","AwayTeam":"Fountain Gate Princess","FullMatchURL":"-","Venue":"-"}]}]}

TEST_JSON_PLAYER = {
    "names": "Test Player",
    "nationality": "Kenyan",
    "dob": "7 August 2023",
    "jersey_num": 2,
    "reg_date": "8 Septemper 2022",
    "team_id": "64d67eb2aa60adcae5ef877d",
    "supporting_file": ""
}

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
    for squad in team:
        for player in team[squad]:
            player_id = ObjectId(player['PlayerID'])
            db_player = db.players.find_one({'_id': player_id})
            if db_player:
                if match_id in db_player['matches']:
                    continue
                stats = db_player['stats']
                stats['match_day_squad'] += 1
                min_played = 0
                if player['starter'] == 'YES':
                    stats['starter'] += 1
                    min_played = 90 if player['SubOut'] == 'NO' else 90 - int(player['SubMinute'])
                    stats['starter_minutes'] += min_played
                elif player['substitute'] == 'YES':
                    min_played = 90 - int(player['SubMinute']) if player['SubIn'] == 'YES' else 0
                    stats['sub_minutes'] += min_played
                stats['min_played'] += min_played
                if player['Goal']:
                    goal_mins = player['GoalMinute'].split(',')
                    for i in range(0, player['Goal']):
                        stats['goals'].append(Goal(minute=goal_mins[i], match_id=match_id).to_mongo())
                db.players.update_one({'_id': player_id},
                                      {'$set': {'stats': stats},
                                       '$addToSet': {'matches': match_id}})


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

        update_player_stats(data['HomeTeam']['Players'], match_id)
        update_player_stats(data['AwayTeam']['Players'], match_id)

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

        name = player_data['names']
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
        player_id = data['player_id']
        old_team_id = data['old_team_id']
        new_team_id = data['new_team_id']
        reg_date = data['reg_date']
        db_player = db.players.find_one({'_id': ObjectId(player_id)})
        if not db_player:
            return edit_html_desc(ERROR_404, 'ID not found in players collection. Check your OID and try again.')
        for team in db_player['teams']:
            if team['team_id']['$oid'] == old_team_id:
                team['team_id']['on_team'] = False
        new_team = PlayerTeam(team_id=new_team_id, reg_date=reg_date, on_team=True)
        db.players.update_one({'_id': ObjectId(player_id)}, {'$addToSet': {'teams': new_team.to_mongo()}})
        db.teams.update_one({'_id': ObjectId(new_team_id)}, {'$addToSet': {'roster': ObjectId(player_id)}})
        db.teams.update_one({'_id': ObjectId(old_team_id)}, {'$pull': {'roster': {'$oid': ObjectId(player_id)}}})
        return append_data(db.players.find_one({'_id': ObjectId(player_id)}), SUCCESS_200)
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
                new_match = Match(date=date, home_team=home_id, away_team=away_id, venue=venue, comp_id=comp_id, match_url=match_url)
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
    app.debug = False
    app.run()
