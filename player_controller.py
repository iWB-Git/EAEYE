from flask import request
import urllib
import os
import copy
import json
from flask import jsonify
from htmlcodes import SUCCESS_200, SUCCESS_201, ERROR_400, ERROR_404, ERROR_405
import mongoengine
from models.player import Player, PlayerTeam
from bson.objectid import ObjectId
import bson.json_util as json_util
import motor.motor_asyncio
from mongoengine.errors import DoesNotExist

# MongoDB setup and initialization
db_username = urllib.parse.quote_plus(os.environ['DB_USERNAME'])
db_password = urllib.parse.quote_plus(os.environ['DB_PASSWORD'])
# db_uri = os.environ['DB_URI'] % (db_username, db_password)
db_uri = os.environ['DB_URI'].format(username=db_username, password=db_password)
db = mongoengine.connect(alias='default', host=db_uri)

# reference to ea_eye database
db = db.ea_eye
# reference to short_report collection in the ea_eye database
player_collection = db.players

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
    # update 'data' field of copied html_response with JSON-formatted string (to_bytes).
    response[0]['data'] = to_bytes
    # returns modified html_response
    return response


# fetching player details
def fetch_player_details(player_id):
    try:
        # Try to find player with the given ID
        player = db.players.find_one({'_id': player_id})
        # Return the extracted details
        print(player)
        return player

    except DoesNotExist:
        # If player not found, return an error message
        return {'error': 'Player not found'}
