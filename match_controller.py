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


# fetching match details
def fetch_match_details(match_id,db):
    try:
        # Try to find a match with the given ID
        match = db.matches.find_one({'_id': match_id})

        return match

    except DoesNotExist:
        # If match not found, return an error message
        return {'error': 'Match not found'}
