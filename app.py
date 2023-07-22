import copy
import urllib
from flask import Flask  # , request, jsonify, stream_with_context, render_template
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bson.json_util as json_util
import json
import data_parse_methods
from html_responses import *
from logging.config import dictConfig
import os
# import json
# from templates import Player
# import yaml
# from bson.objectid import ObjectId
# from requests_html import HTMLSession
# import requests
test_json = {"Team_A":{"Name":"Foxes","Players":{"Starters":[{"Name":"Lightning Mcqueen","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":""},{"Name":"David Degea","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":""}],"Subbed":[]}},"Team_B":{"Name":"Lions","Players":{"Starters":[{"Name":"Harry Maguire","SubOut":"NO","SubMinute":"-","Goal":0,"GoalMinute":""},{"Name":"Bruno Fernandes","SubOut":"YES","SubMinute":"53","Goal":0,"GoalMinute":""}],"Subbed":[]}},"Competition":{"Name":"Piston Cup","Year":"2005","Round":"2","Fixture":"12"}}
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

# application setup
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db_username = urllib.parse.quote_plus(os.environ['DB_USERNAME'])
db_password = urllib.parse.quote_plus(os.environ['DB_PASSWORD'])
db_uri = os.environ['DB_URI'] % (db_username, db_password)

DIRECT_USERNAME = os.environ['URL_DIRECT_USERNAME']
DIRECT_PASSWORD = os.environ['URL_DIRECT_PASSWORD']
TONY_USERNAME = os.environ['TONY_DIRECT_USERNAME']

# Create a new client and connect to the server
client = MongoClient(db_uri, server_api=ServerApi('1'))
db = client.ea_eye

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


@app.route('/')
def index():
    return '<h1>EA Eye API</h1>' \
           '<p>Please contact administrator for access</p>'


@app.route('/api/v1/clear-collection/<collection>/<username>/<password>', methods=['DELETE'])
def clear_db_docs(collection, username, password):
    if (username == DIRECT_USERNAME or username == TONY_USERNAME) and password == DIRECT_PASSWORD:
        db[collection].delete_many({})
        return success_200, 200
    else:
        return error_404, 404


@app.route('/api/v1/upload-match-data/<data>', methods=['POST'])
def upload_match_data(data):
    try:
        data = json.loads(data)
        data_parse_methods.parse_match_data(data)
        return success_201, 201
    except Exception as err:
        print('ERROR LOADING MATCH DATA: ' + str(err))
        return error_400, 400


@app.route('/api/v1/get-player-data/all', methods=['GET'])
def get_all_player_data():
    docs = list(db.players.find({}, {'_id': 0}))
    to_bytes = json_util.dumps(docs)
    response = copy.deepcopy(success_200)
    response['data'] = to_bytes
    return response, 200


if __name__ == '__main__':
    # parse_match_data(test_json)
    app.debug = False
    app.run()
