import asyncio
import copy
import traceback
import urllib
from flask import Flask, request
from flask_cors import CORS
import bson.json_util as json_util
import json
from htmlcodes import *
from logging.config import dictConfig
from models.competition import Competition
from models.player import Player, PlayerTeam, Stats, Goal
from models.match import Match, MatchStats
from models.fixture import Fixture, Round
from models.team import Team
import os
import mongoengine
from bson.objectid import ObjectId
import motor.motor_asyncio

DB_COLLECTIONS = [
    'players',
    'teams',
    'competitions',
    'matches',
    'fixtures',
    'bodies'
]

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
client = motor.motor_asyncio.AsyncIOMotorClient(db_uri)
db_0 = client.ea_eye


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
    return '<h1>Lighthouse Sports API</h1>' \
           '<p>Please contact administrator for access</p>'


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
        # match_id = match_id if type(match_id) is ObjectId else ObjectId(match_id)
        match_id = return_oid(match_id)
        # home_id = home_id if type(home_id) is ObjectId else ObjectId(home_id)
        home_id = return_oid(home_id)
        # away_id = away_id if type(away_id) is ObjectId else ObjectId(away_id)
        away_id = return_oid(away_id)

        # add match id to team's list of played matches
        db.teams.update_many({'_id': {'$in': [home_id, away_id]}}, {'$addToSet': {'matches': match_id}})
        # db.teams.update_one({'_id': home_id}, {'$addToSet': {'matches': match_id}})
        # db.teams.update_one({'_id': away_id}, {'$addToSet': {'matches': match_id}})

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
    if collection not in DB_COLLECTIONS:
        return edit_html_desc(ERROR_404, 'Specified collection does not exist.')
    docs = db[collection].find({})
    if collection in ['players', 'teams', 'competitions']:
        docs = sorted(docs, key=lambda x: x['name'])
    return append_data(docs, SUCCESS_200)


def mark_or_restore_doc(doc_id, coll, to_delete):
    # set the to be deleted document's id and collection, then query for the targeted document
    tbd_id = ObjectId('64d67eb2aa60adcae5ef877d') if coll == 'players' else ObjectId('6526f76a8e4142135d3ffc70')
    tbd_coll = 'teams' if coll == 'players' else 'competitions'
    db_doc = db[coll].find_one({'_id': doc_id})

    # check if the document exists and check if the given collection is supported
    if not db_doc:
        return edit_html_desc(
            ERROR_400,
            'Document not found in database, please check your ID string and try again'
        )
    elif coll not in ['players', 'teams']:
        return edit_html_desc(
            ERROR_400,
            'Specified collection not supported yet; currently supported collections are \'players\' and \'teams\''
        )

    # if the target doc is to be deleted then add it to the TBD document, else remove it from the TBD doc
    if to_delete:
        db[tbd_coll].update_one({'_id': tbd_id}, {'$addToSet': {'documents': doc_id}})
    else:
        db[tbd_coll].update_one({'_id': tbd_id}, {'$pull': {'documents': doc_id}})

    return SUCCESS_200


# mark a document for deletion
# does not alter the database in any way aside from adding the document to a list of others up for deletion
# allows admins to review documents before deletion, or to restore a document without issue
@app.route('/api/v2/mark-for-deletion', methods=['POST'])
def mark_for_deletion():
    try:
        data = json.loads(request.data)
        return mark_or_restore_doc(
            doc_id=return_oid(data['_id']),
            coll=data['collection'],
            to_delete=True
        )
    except Exception as e:
        print_and_return_error(e)


# unmark a document for deletion
# removes the document from the respective TO BE DELETED document's reference list
@app.route('/api/v2/restore-document', methods=['POST'])
def restore_document():
    try:
        data = json.loads(request.data)
        return mark_or_restore_doc(
            doc_id=return_oid(data['_id']),
            coll=data['collection'],
            to_delete=False
        )
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/unattach-document', methods=['POST'])
def unattach_document():
    try:
        data = json.loads(request.data)
        coll = data['collection']
        doc_id = return_oid(data['_id'])
        unattached_id = ObjectId('64de3499f3163e410d0e991a') if coll == 'players' else ObjectId('65285a798e4142135d3ffca8')
        db_doc = db[coll].find_one({'_id': doc_id})
        if not db_doc:
            return edit_html_desc(
                ERROR_400,
                'Document not found in database; please check your ID string and try again'
            )
        if coll == 'players':
            team_ids = []
            for team in db_doc['teams']:
                team_ids.append(return_oid(team['team_id']))
                team['on_team'] = False
            if team_ids:
                db.teams.update_many({'_id': {'$in': team_ids}}, {'$pull': {'roster': doc_id}})
            db.teams.update_one({'_id': unattached_id}, {'$addToSet': {'roster': doc_id}})
            db[coll].update_one({'_id': doc_id}, {'$set': db_doc})
            return SUCCESS_200
        elif coll == 'teams':
            pass
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/delete-player/<player_id>', methods=['POST'])
def delete_player(player_id):
    try:
        # check for the player's document in the database, return bad request code if so
        db_player = db.players.find_one({'_id': player_id})
        if not db_player:
            return edit_html_desc(
                ERROR_400,
                'Player not found in database; please check your ID string and try again'
            )

        # check for duplicate entries in the database
        # for a player check if they have the same name and dob, and a unique id from the given id
        dupes = list(
            db.players.find(
                {
                    'name': db_player['name'],
                    'dob': db_player['dob'],
                    '_id': {'$ne': player_id}
                })
        )

        # if any duplicates exist return a 400 error and append the duplicate documents in question for review
        if dupes:
            return append_data(
                dupes,
                edit_html_desc(
                    ERROR_400,
                    'Duplicate entries exist in database; please review these before continuing'
                )
            )

        # check the teams collection for any teams whose roster contain the given player's id
        id_pairs = list(db.teams.find({'roster': player_id}, {'_id': 1}))

        # generate a list of strictly the ObjectId strings, as opposed to key-value pairs of {'_id': *id_string*}
        team_ids = []
        for pair in id_pairs:
            team_ids.append(pair['_id'])

        # remove the player's id from all the teams identified above
        db.teams.update_many(
            {'_id': {'$in': team_ids}},
            {'$pull': {'roster': player_id}}
        )

        # delete the player document from the database
        db.players.delete_one({'_id': player_id})
        return SUCCESS_200
    except Exception as e:
        print_and_return_error(e)


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


@app.route('/api/v2/insert-doc/', methods=['POST'])
def insert_doc():
    try:
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
            name = data['name'].strip().title()
            comp_id = return_oid(data['competition_id'])
            new_team = Team(name=name, roster=None, matches=None, comps=[comp_id])
            db.teams.insert_one(new_team.to_mongo())
        elif collection == 'competitions':
            name = data['name'].strip().title()
            new_comp = Competition(name=name, teams=[], body_id=None)
            db.competitions.insert_one(new_comp.to_mongo())
        return SUCCESS_201
    except Exception as e:
        return print_and_return_error(e)


@app.route('/api/v2/update-doc/', methods=['POST'])
def update_doc():
    try:
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
    except Exception as e:
        return print_and_return_error(e)


@app.route('/api/v2/create-team/', methods=['POST'])
def create_team():
    try:
        data = json.loads(request.data)
        comp_id = return_oid(data['competition_id'])
        db.teams.insert_one(
            Team(
                name=data['name'].strip().title(),
                roster=[],
                matches=[],
                comps=[comp_id]
            ).to_mongo()
        )
        return SUCCESS_201
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/update-team-name/', methods=['POST'])
def update_team_name():
    try:
        data = json.loads(request.data)
        team_id = return_oid(data['teamId'])
        db.teams.update_one({'_id': team_id}, {'$set': {'name': data['name'].strip().title()}})
        return edit_html_desc(SUCCESS_200, db.teams.find_one({'_id': team_id}))
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/link-team-and-competition/', methods=['POST'])
def link_team_and_competition():
    try:
        data = json.loads(request.data)
        team_id = return_oid(data['teamId'])
        comp_id = return_oid(data['competition_id'])
        db.teams.update_one({'_id': team_id}, {'$addToSet': {'comps': comp_id}})
        db.competitions.update_one({'_id': comp_id}, {'$addToSet': {'teams': team_id}})
        return SUCCESS_201
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/unlink-team-and-competition/', methods=['POST'])
def unlink_team_and_competition():
    try:
        data = json.loads(request.data)
        team_id = return_oid(data['teamId'])
        comp_id = return_oid(data['competition_id'])
        db.teams.update_one({'_id': team_id}, {'$pull': {'comps': comp_id}})
        db.competitions.update_one({'_id': comp_id}, {'$pull': {'teams': team_id}})
        return SUCCESS_200
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/create-competition/', methods=['POST'])
def create_competition():
    try:
        data = json.loads(request.data)
        body_id = return_oid(data['bodyId'])
        db.competitions.insert_one(
            Competition(
                name=data['competition_name'],
                teams=[],
                body_id=body_id
            ).to_mongo()
        )
        return SUCCESS_201
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/update-competition-name/', methods=['POST'])
def update_competition_name():
    try:
        data = json.loads(request.data)
        comp_id = return_oid(data['competitionId'])
        db.competitions.update_one({'_id': comp_id}, {'$set': {'name': data['competition_name'].strip().title()}})
        return SUCCESS_201
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/link-competition-and-body/', methods=['POST'])
def link_competition_and_body():
    try:
        data = json.loads(request.data)
        comp_id = return_oid(data['competition_id'])
        body_id = return_oid(data['bodyId'])
        db.competitions.update_one({'_id': comp_id}, {'$set': {'body_id': body_id}})
        db.body.update_one({'_id': body_id}, {'$addToSet': {'competitions': comp_id}})
        return SUCCESS_201
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/unlink-competition-and-body/', methods=['POST'])
def unlink_competition_and_body():
    try:
        data = json.loads(request.data)
        comp_id = return_oid(data['competition_id'])
        body_id = return_oid(data['bodyId'])
        db.competitions.update_one({'_id': comp_id}, {'$set': {'body_id': None}})
        db.bodies.update_one({'_id': body_id}, {'$pull': {'competitions': comp_id}})
        return SUCCESS_200
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/get-doc/', methods=['GET'])
def get_doc():
    try:
        data = json.loads(request.data)
        collection = data['collection']
        _id = return_oid(data['_id'])
        db_doc = db[collection].find_one({'_id': _id})
        return append_data(db_doc, SUCCESS_200)
    except Exception as e:
        return print_and_return_error(e)


@app.route('/api/v2/delete-doc/', methods=['DELETE'])
def delete_doc():
    try:
        data = json.loads(request.data)
        db[data['collection']].delete_one({'_id': return_oid(data['_id'])})
        return SUCCESS_200
    except Exception as e:
        return print_and_return_error(e)


def print_and_return_error(e):
    traceback.print_exception(type(e), e, e.__traceback__)
    return edit_html_desc(ERROR_400, str(e))


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
            return edit_html_desc(SUCCESS_200,
                                  'This player already exists in the database. Please use move player instead')

        db_team = db.teams.find_one({'_id': ObjectId(player_data['team_id'])})

        new_player = Player(
            name=name,
            dob=dob,
            nationality=nationality,
            jersey_num=jersey_num,
            supporting_file=supporting_file,
            position=position
        )
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
        try:
            player_id = data['player_id'] if type(data['player_id']) is ObjectId else ObjectId(data['player_id'])
            db_player = db.players.find_one({'_id': player_id})
        except KeyError as e:
            print('request.data :: ' + str(request.data))
            print('data :: ' + str(data))
            return edit_html_desc(append_data(data, ERROR_400), 'Player was passed without an ID.\nError: ' + str(e))
        if not db_player:
            return edit_html_desc(ERROR_404, 'ID not found in players collection. Check your OID and try again.')

        # check if player has a team they are being moved from. if yes, update the player's team list and update
        # the team's roster. if not, do nothing and move on to adding the new team and updating its roster
        if data['old_team_id'] == '':
            pass
        else:
            old_team_id = data['old_team_id'] if type(data['old_team_id']) is ObjectId else ObjectId(
                data['old_team_id'])
            db.players.update_one({'_id': player_id, 'teams.team_id': old_team_id},
                                  {'$set': {'teams.$.on_team': False}})
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
        try:
            _id = return_oid(new_doc['_id'])
        except KeyError as e:
            print('request.data :: ' + str(request.data))
            print('data :: ' + str(new_doc))
            return edit_html_desc(append_data(new_doc, ERROR_400), 'Request data has no _id key.\nError: ' + str(e))
        db_doc = db[collection].find_one({'_id': _id})
        if not db_doc:
            return edit_html_desc(ERROR_404, 'ID not found in given collection. Check your OID and try again.')
        new_values = {}
        for key in new_doc:
            if key == '_id':
                continue
            if not new_doc[key] == db_doc[key]:
                new_values[key] = new_doc[key]
        db[collection].update_one({'_id': _id}, {'$set': new_values})
        updated_doc = db[collection].find_one({'_id': _id})
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
                new_match = Match(competition_id=comp_id, home_team=home_id, away_team=away_id, date=date, venue=venue,
                                  match_url=match_url)
                match_ids.append(db.matches.insert_one(new_match.to_mongo()).inserted_id)
            new_round = Round(matchups=match_ids)
            new_fixture['rounds'].append(new_round.to_mongo())
        db.fixtures.insert_one(new_fixture.to_mongo())
        return SUCCESS_201
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))


@app.route('/api/v2/upload-csv/fixtures', methods=['POST'])
def upload_fixture_csv():
    try:
        # comp_id = return_oid(db.competitions.find_one({'name': data['competition_name'].strip().title()}))
        data = json.loads(request.data)
        db_comp = db.competitions.find_one({'name': data['competition_name'].strip().title()})
        if not db_comp:
            return edit_html_desc(ERROR_404, 'Specified competition not found, please check your entry and try again')
        comp_id = return_oid(db_comp['_id'])
        new_fixture = Fixture(competition=comp_id, comp_year=data['competition_year'], rounds=[])
        for round in data['round_data']:
            new_round = Round(matchups=[])
            print('ROUND: ' + str(round['round']) + '\n\n')
            for i in range(0, len(round['round_data'])):
                print(round['round_data'][i])
                home_id = return_oid(db.teams.find_one({'name': round['round_data'][i]['HomeTeam']})['_id'])
                away_id = return_oid(db.teams.find_one({'name': round['round_data'][i]['AwayTeam']})['_id'])
                new_match = Match(
                    competition_id=comp_id,
                    home_team=home_id,
                    away_team=away_id,
                    date=round['round_data'][i]['Date'],
                    venue=round['round_data'][i]['Venue'],
                    match_url=round['round_data'][i]['FullMatchURL']
                )
                match_id = db.matches.insert_one(new_match.to_mongo()).inserted_id
                db.teams.update_many({'_id': {'$in': [home_id, away_id]}}, {'$addToSet': {'matches': match_id}})
                new_round['matchups'].append(match_id)
            new_fixture['rounds'].append(new_round.to_mongo())
        db.fixtures.insert_one(new_fixture.to_mongo())
        return SUCCESS_201
    except Exception as e:
        print_and_return_error(e)


@app.route('/api/v2/upload-csv/players', methods=['POST'])
def upload_players_csv():
    try:
        data = json.loads(request.data)
        for team in data:
            player_ids = []
            db_team = db.teams.find_one({'name': team['team'].strip().title()})
            if not db_team:
                continue
            team_id = return_oid(db_team['_id'])
            for player in team['player_data']:
                db_player = db.players.find_one({'name': player['Name'].strip().title()})
                if db_player:
                    if db_player['jersey_num'] == player['JerseyNo'] and db_player['dob'] == player['DateOfBirth']:
                        continue
                new_player = Player(
                    name=player['Name'].strip().title(),
                    dob=player['DateOfBirth'],
                    nationality=player['Nationality'],
                    jersey_num=player['JerseyNo'],
                    supporting_file=None,
                    position=None
                )
                player_team = PlayerTeam(
                    team_id=team_id,
                    reg_date=player['RegistrationDate'],
                    on_team=True
                )
                new_player['teams'].append(player_team.to_mongo())
                player_ids.append(db.players.insert_one(new_player.to_mongo()).inserted_id)
            db.teams.update_one({'_id': team_id}, {'$addToSet': {'roster': player_ids}})
        return SUCCESS_201
    except Exception as e:
        print_and_return_error(e)


if __name__ == '__main__':
    app.debug = False
    app.run()
