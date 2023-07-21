import urllib
from flask import Flask, request, jsonify, stream_with_context  # , render_template
# import json
# from bson.objectid import ObjectId
from flask_cors import CORS
# import yaml
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bson.json_util as json_util
# import requests
# from requests_html import HTMLSession
import json
import html_responses
from logging.config import dictConfig

# mongodb data api key: cGdNPmHgqm5MwWIrS9hgDPbUTl0GK38e9pPSbYAnYwwARTuC6A6v4veLUG9eRUq5
# bryce-ea-eye password: nyDPeA2WcbpDmAJG

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

DIRECT_USERNAME = 'brucetopher'
DIRECT_PASSWORD = 'wordpassword'

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
    parse_team_data(team_one)
    parse_team_data(team_two)


def parse_team_data(team_data):
    team_keys = list(team_data.keys())
    # team_name = team_data[team_keys[0]]
    team_players = team_data[team_keys[1]]
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
    return '<h1>EA Eye API</h1>' \
           '<p>Please contact administrator for access</p>'


@app.route('/api/v1/clear-collection/<collection>/<username>/<password>', methods=['DELETE'])
def clear_db_docs(collection, username, password):
    if not request.method == 'DELETE':
        return html_responses.request_not_permitted, 405
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
        return response, 404


@app.route('/api/v1/upload-match-data/<data>', methods=['POST'])
def upload_match_data(data):
    if not request.method == 'POST':
        return html_responses.request_not_permitted, 405
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


@app.route('/api/v1/get-player-data/all', methods=['GET'])
def get_all_player_data():
    if not request.method == 'GET':
        return html_responses.request_not_permitted, 405
    docs = list(db.players.find({}, {'_id': 0}))
    to_bytes = json_util.dumps(docs)
    return to_bytes, 200


if __name__ == '__main__':
    app.debug = False
    app.run()
