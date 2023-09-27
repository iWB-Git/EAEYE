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
from models.competition import Competition
from models.player import Player, PlayerTeam, Stats, Goal
from models.match import Match, MatchStats
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
# from country_parse import upload_countries
# from fixture_csv_parse import parse_fixtures

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


def return_oid(_id):
    return _id if type(_id) is ObjectId else ObjectId(_id)


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


@app.route('/api/v1/clear-team-stats/<team_id>/<username>/<password>', methods=['DELETE'])
def clear_team_stats(team_id, username, password):
    if (username == DIRECT_USERNAME or username == TONY_USERNAME) and password == DIRECT_PASSWORD:
        db_team = db.teams.find_one({'_id': ObjectId(team_id)})
        for player_id in db_team['roster']:
            db.players.update_one({'_id': player_id}, {'$set': {'stats': Stats().to_mongo(), 'matches': []}})
        db.teams.update_one({'_id': ObjectId(team_id)}, {'$set': {'matches': []}})
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

    # get match id and ensure it's the correct type, and set up the stats list to return at the end
    # match_id = match_id if type(match_id) is ObjectId else ObjectId(match_id)
    stats_list = []

    # squad: starters vs. subbed
    for squad in team:

        # each player that was in the starters or subbed list
        for player in team[squad]:

            # get player id and find that player in the db, if they have this match recorded somehow then skip
            player_id = ObjectId(player['PlayerID'])
            db_player = db.players.find_one({'_id': player_id})
            if db_player:
                if match_id in db_player['matches']:
                    continue

                # create player_stats to increment career stats and match_stats to record just this match's stats
                career_stats = db_player['stats']
                match_stats = MatchStats(match_id=match_id, player_id=player_id)

                # increment number of match day squads and set min_played to 0
                career_stats['match_day_squad'] += 1
                min_played = 0

                # if the player is a starter, increment their starter count and calculate minutes played
                # min_played is 90 if they started and never came out, else equal to the minute they subbed out
                # increment starter minutes by min_played and flip the single match stat starter parameter to true
                if player['starter'] == 'YES':
                    career_stats['starter'] += 1
                    min_played = 90 if player['SubOut'] == 'NO' else int(player['SubMinute'])
                    career_stats['starter_minutes'] += min_played
                    match_stats['starter'] = True

                # if the player was a sub, their min_played are equal to 0 unless they subbed in
                # if subbed in, min_played is equal to 90 - their sub in time
                # increment their sub minutes by min_played
                elif player['substitute'] == 'YES':
                    min_played = 90 - int(player['SubMinute']) if player['SubIn'] == 'YES' else 0
                    career_stats['sub_minutes'] += min_played

                # increment career stats by min_played and set match_stats to min_played
                career_stats['min_played'] += min_played
                match_stats['min_played'] = min_played

                # if the player scored a goal, split goal minutes list by ',' and loop for how many they scored
                # creating a new goal object each time and appending them to both career and match stats goals lists
                if player['Goal']:
                    goal_mins = player['GoalMinute'].split(',')
                    for i in range(0, int(player['Goal'])):
                        goal = Goal(minute=int(goal_mins[i]), match_id=match_id)
                        career_stats['goals'].append(goal.to_mongo())
                        match_stats['goals'].append(goal.to_mongo())

                # update the player's career stats
                db.players.update_one({'_id': player_id},
                                      {
                                          '$set': {
                                              'stats': career_stats
                                          },
                                          '$addToSet': {
                                              'matches': match_id
                                          }
                                      })

                # append the player's match stats to the list of all player's match stats
                stats_list.append(match_stats.to_mongo())

    # return this team's individual player's match stats in a list to be uploaded to the match document
    return stats_list


# TODO: INCREMENT A TOTAL POSSIBLE GAMES COUNTER FOR ALL PLAYERS ON TEAM WHO WERE NOT MATCH DAY SQUAD
@app.route('/api/v2/upload-match-data', methods=['POST'])
def upload_match_data_v2():
    try:
        # load in match data from html request
        data = json.loads(request.data)

        # get relevant match and team id's and perform type checking/casting for safety
        match_id = data['Competition']['MatchID']
        home_id = data['HomeTeam']['teamID']
        away_id = data['AwayTeam']['teamID']
        match_id = match_id if type(match_id) is ObjectId else ObjectId(match_id)
        home_id = home_id if type(home_id) is ObjectId else ObjectId(home_id)
        away_id = away_id if type(away_id) is ObjectId else ObjectId(away_id)

        # add match id to team's list of played matches
        db.teams.update_one({'_id': home_id}, {'$addToSet': {'matches': match_id}})
        db.teams.update_one({'_id': away_id}, {'$addToSet': {'matches': match_id}})

        # update the stats for each player on the home and away teams
        home_stats = update_player_stats(data['HomeTeam']['Players'], match_id)
        away_stats = update_player_stats(data['AwayTeam']['Players'], match_id)

        # add each team's individual player's match stats to the match document in the db
        db.matches.update_one({'_id': match_id},
                              {
                                  '$set': {
                                      'data_entered': True,
                                      'home_stats': home_stats,
                                      'away_stats': away_stats
                                  }
                              })

        return SUCCESS_200

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/get-collection/<collection>', methods=['GET'])
def get_collection(collection):
    if collection not in db.list_collection_names():
        return edit_html_desc(ERROR_404, 'Specified collection does not exist.')
    docs = db[collection].find({})
    if collection in ['players', 'teams', 'competitions']:
        docs = sorted(docs, key=lambda x: x['name'])
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


@app.route('/api/v1/get-competitions-from-body', methods=['GET'])
def get_comps_from_body():
    try:
        data = json.loads(request.data)
        body_id = data['body_id'] if type(data['body_id']) is ObjectId else ObjectId(data['body_id'])
        db_body = db.bodies.find_one({'_id': body_id})
        return append_data(db_body['competitions'], SUCCESS_200)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)


@app.route('/api/v1/get-team-match-entries', methods=['GET'])
def get_team_match_entries():
    try:
        data = json.loads(request.data)
        team_id = data['team_id'] if type(data['team_id']) is ObjectId else ObjectId(data['team_id'])
        db_team = db.teams.find_one({'_id': team_id})
        return append_data(db_team['matches'], SUCCESS_200)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v1/get-stats-from-match', methods=['GET'])
def get_stats_from_match():
    try:
        # match_id = ObjectId(match_id)
        data = json.loads(request.data)
        match_id = data['match_id'] if type(data['match_id']) is ObjectId else ObjectId(data['match_id'])
        db_match = db.matches.find_one({'_id': match_id})
        return append_data({'home_stats': db_match['home_stats'], 'away_stats': db_match['away_stats']}, SUCCESS_200)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


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
        players = sorted(list(db.players.find({'_id': {'$in': ids}})), key=lambda x: x['name'])
        return append_data(players, SUCCESS_200)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


def check_for_duplicate_player(name, dob, jersey_num):
    db_players = list(db.players.find({'name': name}))
    for player in db_players:
        if player['dob'] == dob:
            if player['jersey_num'] == jersey_num:
                return True
    return False


@app.route('/api/v2/create-document', methods=['POST'])
def create_document():
    data = json.loads(request.data)
    collection = data['collection']
    if collection not in db.list_collection_names():
        return edit_html_desc(ERROR_400, 'Specified collection/document type does not exist')
    if collection == 'players':
        name = data['names'].strip().title()
        nationality = data['nationality']
        dob = data['dob']
        position = data['position']
        jersey_num = data['jersey_num']
        supporting_file = data['supporting_file']
        reg_date = data['reg_date']
        team_id = return_oid(data['team_id'])
        db_team = db.teams.find_one({'_id': team_id})
        new_player = Player(
            name=name,
            dob=dob,
            nationality=nationality,
            jersey_num=jersey_num,
            supporting_file=supporting_file,
            position=position
        )
        player_club = PlayerTeam(
            team_id=db_team['_id'],
            teg_date=reg_date,
            on_team=True
        )
        new_player['teams'].append(player_club.to_mongo())
        db_player = db.players.insert_one(new_player.to_mongo())
        db.teams.update_one({'_id': db_team['_id']}, {'$addToSet': {'roster': db_player.inserted_id}})
    elif collection == 'teams':
        name = data['name']
        comp_id = return_oid(data['competition_id'])
        new_team = Team(name=name, roster=None, matches=None, comps=[comp_id])
        db.teams.insert_one(new_team.to_mongo())
    elif collection == 'competitions':
        name = data['name']
        new_comp = Competition(name=name, teams=[])
        db.competitions.insert_one(new_comp.to_mongo())
    return SUCCESS_201


@app.route('/api/v1/insert-player/', methods=['POST'])
def insert_player():
    try:
        player_data = json.loads(request.data)
        # player_data = TEST_JSON_PLAYER

        name = player_data['names'].strip().title()
        nationality = player_data['nationality']
        dob = player_data['dob']
        position = player_data['position']
        jersey_num = player_data['jersey_num']
        supporting_file = player_data['supporting_file']
        reg_date = player_data['reg_date']

        if check_for_duplicate_player(name, dob, jersey_num):
            return edit_html_desc(SUCCESS_200, 'This player already exists in the database. Please use move player instead')

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

        # load json data into dict
        data = json.loads(request.data)

        # check type of player_id to ensure it's stored as an ObjectId, then query the db for that player
        # if no player exists return immediately indicating the missing player
        player_id = data['player_id'] if type(data['player_id']) is ObjectId else ObjectId(data['player_id'])
        db_player = db.players.find_one({'_id': player_id})
        if not db_player:
            return edit_html_desc(ERROR_404, 'ID not found in players collection. Check your OID and try again.')

        # check if player has a team they are being moved from. if yes, update the player's team list and update
        # the team's roster. if not, do nothing and move on to adding the new team and updating its roster
        if data['old_team_id'] == '':
            pass
        else:
            old_team_id = data['old_team_id'] if type(data['old_team_id']) is ObjectId else ObjectId(data['old_team_id'])
            db.players.update_one({'_id': player_id, 'teams.team_id': old_team_id}, {'$set': {'teams.$.on_team': False}})
            db.teams.update_one({'_id': old_team_id}, {'$pull': {'roster': player_id}})

        new_team_id = data['new_team_id'] if type(data['new_team_id']) is ObjectId else ObjectId(data['new_team_id'])
        reg_date = data['reg_date']

        # create new PlayerTeam embedded doc
        new_team = PlayerTeam(team_id=new_team_id, reg_date=reg_date, on_team=True)

        # update the db as follows:
        # 1. update player's team list to have the new team, and flip the old team's 'on_team' flag to false
        # 2. add the player's id to his new team's roster
        # 3. remove the player's id from his old team
        db.players.update_one({'_id': player_id}, {'$addToSet': {'teams': new_team.to_mongo()}})
        db.teams.update_one({'_id': new_team_id}, {'$addToSet': {'roster': player_id}})

        # return the updated player document to front end
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


@app.route('/api/v2/update-document/', methods=['POST'])
def update_document():
    data = json.loads(request.data)
    collection = data['collection']
    _id = return_oid(data['_id'])
    db_doc = db[collection].find_one({'_id': _id})
    if not db_doc:
        return edit_html_desc(ERROR_404, 'ID not found in players collection. Check your OID and try again.')
    new_vals = {}
    for key in data:
        if key == '_id' or key == 'collection':
            continue
        if not data[key] == db_doc[key]:
            new_vals[key] = data[key]
    db[collection].update_one({'_id': _id}, {'$set': new_vals})
    return append_data(db[collection].find_one({'_id': _id}), SUCCESS_200)


@app.route('api/v2/get-document/', methods=['GET'])
def get_document():
    data = json.loads(request.data)
    db_doc = db[data['collection']].find_one({'_id': return_oid(data['_id'])})
    if not db_doc:
        return edit_html_desc(ERROR_404, 'The specified collection/document pair does not exist, check your ID and try again.')
    return append_data(db_doc, SUCCESS_200)


@app.route('/api/v2/delete-document', methods=['DELETE'])
def delete_document():
    data = json.loads(request.data)
    deleted_doc = db[data['collection']].delete_one({'_id': return_oid(data['_id'])})
    return append_data(deleted_doc, SUCCESS_200)


@app.route('/api/v1/get-teams/<comp_id>', methods=['GET'])
def get_teams_from_comp(comp_id):
    try:
        competition = db.competitions.find_one({'_id': ObjectId(comp_id)})
        if not competition:
            return edit_html_desc(ERROR_404, 'ID not found in competitions collection. Check your OID and try again.')
        team_ids = competition['teams']
        teams = sorted(db.teams.find({'_id': {'$in': team_ids}}), key=lambda x: x['name'])
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
    # test_player = Player(name='test', dob='testdob', nationality='testNat', jersey_num='', supporting_file='asdf', position='pog')
    # print(test_player.to_mongo().to_dict())
    # db_team = db.teams.find_one({'_id': ObjectId('64d52c9f4cdabb9dfc3b4a60')})
    # unique_ids = list(set(db_team['roster']))
    # db_players = db.players.find({'_id': {'$in': unique_ids}})
    # unique_names = set()
    # for player in db_players:
    #     unique_names.add(player['name'].strip().title())
    # for name in sorted(unique_names):
    #     print(name)
    # upload_countries()
    # comp_list = db.competitions.find({})
    # for comp in comp_list:
    #     db.competitions.update_one({'_id': comp['_id']}, {'$set': {'body_id': None}})

    # roster = db.teams.find_one({'name': 'Simba Sports Club'})['roster']
    # players = db.players.find({'_id': {'$in': roster}})
    # unique = []
    # duplicates = []
    # filename = '/Users/brycesczekan/PycharmProjects/ea-eye-api/static/tz_fixtures.csv'
    # parse_fixtures(filename)
    app.debug = False
    app.run()
