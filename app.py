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
from models.player import Player
from models.player import PlayerTeam
from models.match import Match
from models.team import Team
import os
import mongoengine
from datetime import datetime
# import json
# from templates import Player
# import yaml
from bson.objectid import ObjectId
# from requests_html import HTMLSession
# import requests
# from csv_parse import read_csv

TEST_JSON_LONG = {"Team_A":{"Name":"Team A","Players":{"Starters":[{"Name":"John Smith","SubOut":"YES","SubMinute":"34","Goal":3,"GoalMinute":"25,37,72","JerseyNumber":10,"checkId":"leftStarterCheck0","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Michael Johnson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":7,"checkId":"leftStarterCheck1","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Robert Davis","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":14,"checkId":"leftStarterCheck2","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"David Wilson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":5,"checkId":"leftStarterCheck3","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Daniel Thompson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":3,"checkId":"leftStarterCheck4","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Christopher Martinez","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":9,"checkId":"leftStarterCheck5","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Matthew Anderson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":23,"checkId":"leftStarterCheck6","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Andrew Taylor","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":16,"checkId":"leftStarterCheck7","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Joseph Clark","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":18,"checkId":"leftStarterCheck8","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"James Thomas","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":21,"checkId":"leftStarterCheck9","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Steven Walker","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":2,"checkId":"leftStarterCheck10","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"}],"Subbed":[{"Name":"Richard Rodriguez","SubIn":"YES","SubMinute":"34","Goal":0,"GoalMinute":"-","JerseyNumber":8,"checkId":"leftSubCheck11","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Paul Young","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":11,"checkId":"leftSubCheck12","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Mark Hall","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":6,"checkId":"leftSubCheck13","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Kevin Green","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":4,"checkId":"leftSubCheck14","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Anthony Harris","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":13,"checkId":"leftSubCheck15","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Charles White","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":17,"checkId":"leftSubCheck16","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Kenneth King","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":19,"checkId":"leftSubCheck17","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"George Lewis","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":20,"checkId":"leftSubCheck18","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Edward Turner","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":22,"checkId":"leftSubCheck19","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Thomas Hill","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":1,"checkId":"leftSubCheck20","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Brian Scott","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":15,"checkId":"leftSubCheck21","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"William Walker","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":12,"checkId":"leftSubCheck22","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"}]}},"Team_B":{"Name":"Team B","Players":{"Starters":[{"Name":"Daniel Brown","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":26,"checkId":"rightStarterCheck0","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Andrew Johnson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":27,"checkId":"rightStarterCheck1","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Christopher Davis","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":28,"checkId":"rightStarterCheck2","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Joseph Wilson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":29,"checkId":"rightStarterCheck3","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Michael Thompson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":30,"checkId":"rightStarterCheck4","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Matthew Thomas","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":31,"checkId":"rightStarterCheck5","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"John Martinez","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":32,"checkId":"rightStarterCheck6","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Robert Anderson","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":33,"checkId":"rightStarterCheck7","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"James Clark","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":34,"checkId":"rightStarterCheck8","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"David Taylor","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":35,"checkId":"rightStarterCheck9","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"},{"Name":"Christopher Walker","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":36,"checkId":"rightStarterCheck10","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"YES","substitute":"NO"}],"Subbed":[{"Name":"Steven Rodriguez","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":37,"checkId":"rightSubCheck11","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Richard Young","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":38,"checkId":"rightSubCheck12","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Mark Hall","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":39,"checkId":"rightSubCheck13","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Kevin Green","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":40,"checkId":"rightSubCheck14","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Anthony Harris","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":41,"checkId":"rightSubCheck15","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Charles White","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":42,"checkId":"rightSubCheck16","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Kenneth King","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":43,"checkId":"rightSubCheck17","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"George Lewis","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":44,"checkId":"rightSubCheck18","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Edward Turner","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":45,"checkId":"rightSubCheck19","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Thomas Hill","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":46,"checkId":"rightSubCheck20","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"Brian Scott","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":47,"checkId":"rightSubCheck21","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"},{"Name":"William Walker","SubIn":"NO","SubMinute":"-","Goal":0,"GoalMinute":"-","JerseyNumber":48,"checkId":"rightSubCheck22","competitionYear":"2022/2023","competitionName":"FKF Premier League","competitionRound":"Round 1","homeTeam":"Team A","awayTeam":"Team B","matchDaySquad":"YES","starter":"NO","substitute":"YES"}]}},"Competition":{"Name":"FKF Premier League","Year":"2022/2023","Round":"Round 1","Fixture":"Gor Mahia vs AFC"}}

TEST_JSON = {"Team_A":{"Name": "Foxes", "Players":{"Starters":[{"Name": "Lightning Mcqueen", "SubOut": "NO", "SubMinute": "-", "Goal":0, "GoalMinute": ""}, {"Name": "David Degea", "SubOut": "NO", "SubMinute": "-", "Goal":0, "GoalMinute": ""}], "Subbed":[]}}, "Team_B":{"Name": "Lions", "Players":{"Starters":[{"Name": "Harry Maguire", "SubOut": "NO", "SubMinute": "-", "Goal":0, "GoalMinute": ""}, {"Name": "Bruno Fernandes", "SubOut": "YES", "SubMinute": "53", "Goal":0, "GoalMinute": ""}], "Subbed":[]}}, "Competition":{"Name": "Piston Cup", "Year": "2005", "Round": "2", "Fixture": "12"}}

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
    try:
        data = json.loads(request.data)
        match_data_upload.split_match_data(data)
        return SUCCESS_201
    except Exception as e:
        print('ERROR LOADING MATCH DATA: ' + str(e))
        return ERROR_400


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
        players = db.players.find({'_id': {'$in': roster}})
        return append_data(players, SUCCESS_200)
    except Exception as e:
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/insert-player/', methods=['POST'])
def insert_player():
    try:
        player_data = json.loads(request.data)
        name = player_data['names']
        nationality = player_data['nationality']
        dob = player_data['dob']
        jersey_num = player_data['jersey_num']
        supporting_file = player_data['supportingfile']
        team_id = player_data['team_id']
        new_player = Player(name=name, dob=dob, nationality=nationality, jersey_num=jersey_num)
        player_club = PlayerTeam(team_id=ObjectId(team_id), reg_date=None, on_team=True)
        new_player['teams'].append(player_club)
        new_player['supporting_file'] = supporting_file
        db.players.insert_one(new_player.to_mongo)
        return SUCCESS_201
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return ERROR_400


@app.route('/api/v1/update-one/<collection>', methods=['POST'])
def update_player(collection):
    try:
        print('here0')
        new_doc = json.loads(request.data)
        print('here1')
        _id = new_doc['_id']['$oid']
        print(_id)
        db_doc = db[collection].find_one({'_id': ObjectId(_id)})
        print('here2')
        if not db_doc:
            return edit_html_desc(ERROR_404, 'ID not found in players collection. Check your OID and try again.')
        print('here3')
        new_values = {}
        for key in new_doc:
            if key == '_id':
                continue
            if not new_doc[key] == db_doc[key]:
                new_values[key] = new_doc[key]
        print('here4')
        update_result = db[collection].update_one({'_id': ObjectId(_id)}, {'$set': new_values})
        print('here5')
        print(update_result)

        try:
            print('here6')
            print(update_result.raw_result)
            print('here7')
            print(update_result)
        except Exception as e:
            print(e)

        updated_doc = db[collection].find_one({'_id': ObjectId(_id)})
        print('here8')
        return append_data(updated_doc, SUCCESS_200)
    except Exception as e:
        print('here9')
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


if __name__ == '__main__':
    app.debug = False
    app.run()