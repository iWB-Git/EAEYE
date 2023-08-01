import copy
import urllib
from flask import Flask, request  # , jsonify, stream_with_context, render_template
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bson.json_util as json_util
import json
import data_parse_methods
import match_data_upload
from html_responses import *
from logging.config import dictConfig
from models.player import Player
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
# Create a new client and connect to the server
# client = MongoClient(db_uri, server_api=ServerApi('1'))
# db = client.ea_eye
# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)


# brief landing page if someone somehow ends up on the API's home page
@app.route('/')
def index():
    return '<h1>EA Eye API</h1>' \
           '<p>Please contact administrator for access</p>'


# endpoint for devs to quickly clear a MongoDB collection
# <collection>: collection to clear
# <username>: dev's provided username
# <password>: dev's provided password
@app.route('/api/v1/clear-collection/<collection>/<username>/<password>', methods=['DELETE'])
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
        data_parse_methods.parse_match_data(data)
        return SUCCESS_201
    except Exception as err:
        print('ERROR LOADING MATCH DATA: ' + str(err))
        return ERROR_400


# endpoint to retrieve all documents in the players collection
@app.route('/api/v1/get-player-data/all', methods=['GET'])
def get_all_player_data():
    # get list of all players in player collection and format into bytes for JSON response
    docs = list(db.players.find({}, {'_id': 0}))
    to_bytes = json_util.dumps(docs)

    # append JSON byte data to JSON response
    response = copy.deepcopy(SUCCESS_200)
    response[0]['data'] = to_bytes
    return response


if __name__ == '__main__':
    # data_parse_methods.parse_match_data(TEST_JSON)
    # match_data_upload.split_match_data(TEST_JSON)
    # db.matches.insert_one(match.to_dict())
    app.debug = False
    app.run()






    # team_a = Team('test_team_a')
    # db_team = db.teams.insert_one(team_a.to_dict())
    # player_a = Player('player_a', 0, 'player_natl_a', 0)
    # player_b = Player('player_b', 1, 'player_natl_b', 1)
    # db_players = db.players.insert_many([player_a.to_dict(), player_b.to_dict()])
    # db.teams.update_one({'name': 'test_team_a'}, {'$set': {'roster': db_players.inserted_ids}})
    # for _id in db_players.inserted_ids:
    #     db.players.update_one({'_id': _id}, {'$addToSet': {'teams_id': db_team.inserted_id}})
    # players = db.players
    # player = players.find_one({'name': 'player_a'})
    # for key in player:
    #     print('key: %s val: %s' % (key, player[key]))






    # team_a = Team('test_team_a')
    # player_a = Player('name_test_a', 0, 'natl_test_a', 0, team_a)
    # player_a.team = ObjectId(team_a.id)
    # player_b = Player('name_test_b', 1, 'natl_test_b', 1, team_a)
    # player_b.team = ObjectId(team_a.id)
    # team_a.roster = [ObjectId(player_a.id), ObjectId(player_b.id)]
    # db.teams.insert_one(team_a.to_dict())
    # db.players.insert_one(player_b.to_dict())
    # db.players.insert_one(player_a.to_dict())
    # found_team = db.teams.find_one({'name': 'test_team_a'})
    # found_player = db.players.find_one({'name': 'name_test_a'})
    # print(found_player)
    # found_player_0 = db.players.find_one({'_id': found_player['_id']})
    # print('found_player_0')
    # print(found_player_0)
    # print(found_team['roster'])
    # for player in found_team['roster']:
    #     print(player)
