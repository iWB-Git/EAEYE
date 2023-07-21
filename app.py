import urllib
from flask import Flask, request  # , jsonify, render_template, request
# import json
# from bson.objectid import ObjectId
from flask_cors import CORS
# import yaml
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# import requests
# from requests_html import HTMLSession
import json

# mongodb data api key: cGdNPmHgqm5MwWIrS9hgDPbUTl0GK38e9pPSbYAnYwwARTuC6A6v4veLUG9eRUq5
# bryce-ea-eye password: nyDPeA2WcbpDmAJG

DIRECT_USERNAME = 'bruce'
DIRECT_PASSWORD = 'word'

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db_username = urllib.parse.quote_plus('bryce-ea-eye')
db_password = urllib.parse.quote_plus('nyDPeA2WcbpDmAJG')
uri = "mongodb+srv://%s:%s@cluster0.umgaluo.mongodb.net/?retryWrites=true&w=majority" % (db_username, db_password)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.ea_eye

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


def parse_match_data(match_data):
    match_keys = list(match_data.keys())
    team_one = match_data[match_keys[0]]
    team_two = match_data[match_keys[1]]
    # comp_data = match_data[match_keys[2]]
    # print('team one: ' + str(team_one) + '\nteam two: ' + str(team_two) + '\ncomp data: ' + str(comp_data) + '\n')
    parse_team_data(team_one)
    parse_team_data(team_two)


def parse_team_data(team_data):
    team_keys = list(team_data.keys())
    # team_name = team_data[team_keys[0]]
    team_players = team_data[team_keys[1]]
    # print('team name: ' + str(team_name) + '\nteam players: ' + str(team_players) + '\n')
    parse_player_data(team_players)


def parse_player_data(player_data):
    player_keys = list(player_data.keys())
    starters = player_data[player_keys[0]]
    bench = player_data[player_keys[1]]

    insert_player_data(starters) if len(starters) \
        else print('ERROR DURING DATA UPLOAD: \"insert_player_data(starters)\": CANNOT UPLOAD EMPTY LIST\n')

    insert_player_data(bench) if len(bench) \
        else print('ERROR DURING DATA UPLOAD: \"insert_player_data(bench)\": CANNOT UPLOAD EMPTY LIST\n')


def insert_player_data(players):
    db_players = db.players
    db_players.insert_many(players)


@app.route('/')
def index():
    html = '<h1>EA Eye API</h1>' \
           '<p>Please contact administrator for access</p>'
    return html


@app.route('/api/v1/clear-collection/<collection>/<username>/<password>', methods=['DELETE'])
def clear_db_docs(collection, username, password):
    if not request.method == 'DELETE':
        response = {
            'status': 'failure',
            'description': 'request type not permitted'
        }
        return response, 405
    elif username == DIRECT_USERNAME and password == DIRECT_PASSWORD:
        db[collection].delete_many({})
        response = {
            'status': 'success',
            'description': 'collection cleared'
        }
        return response, 200
    else:
        response = {
            'status': 'failure',
            'description': 'invalid credentials'
        }
        return response, 405


@app.route('/api/v1/upload-match-data/<data>', methods=['POST'])
def upload_match_data(data):
    try:
        data = json.loads(data)
        parse_match_data(data)
        result = {'status': 'success'}
        return result, 201
    except Exception as err:
        print('ERROR LOADING MATCH DATA: ' + str(err))
        result = {
            'status': 'failure',
            'description': 'the supplied data could not be parsed. please check your formatting and try again'
        }
        return result, 400


@app.route('/api/v1/all-player-data', methods=['GET'])
def get_all_player_data():
    pass


if __name__ == '__main__':
    app.debug = False
    app.run()
