from flask import request
import urllib
import os
import copy
import json
from flask import jsonify
from htmlcodes import SUCCESS_200, SUCCESS_201, ERROR_400, ERROR_404, ERROR_405
import mongoengine
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
match_collection = db.matches

client = motor.motor_asyncio.AsyncIOMotorClient(db_uri)
db_0 = client.ea_eye


# fetching match details
def fetch_match_details(match_id):
    try:
        # Try to find a match with the given ID
        match = db.matches.find_one({'_id': match_id})

        return match

    except DoesNotExist:
        # If match not found, return an error message
        return {'error': 'Match not found'}
