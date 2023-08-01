import pymongo.results

import app
from models.match import Match
from models.player import Player

insert_one_res = pymongo.results.InsertOneResult


# from models.competition import Competition
# from models.player import Player
# TODO: make code more dry


def split_match_data(match_data):
    match_data_keys = list(match_data.keys())
    team_one_data = match_data[match_data_keys[0]]
    team_two_data = match_data[match_data_keys[1]]
    comp_data = match_data[match_data_keys[2]]

    match_doc = create_match_doc(comp_data)

    team_one_data_keys = list(team_one_data.keys())
    team_two_data_keys = list(team_two_data.keys())
    team_one_players = team_one_data[team_one_data_keys[1]]
    team_two_players = team_two_data[team_two_data_keys[1]]

    team_one_doc = create_team_doc(team_one_data)
    team_two_doc = create_team_doc(team_two_data)
    team_one_player_docs = create_player_docs(team_one_players)
    team_two_player_docs = create_player_docs(team_two_players)

    check_player_team_relation(team_one_player_docs, team_one_doc)
    check_player_team_relation(team_two_player_docs, team_two_doc)

    check_team_match_relation(team_one_doc, match_doc)
    check_team_match_relation(team_two_doc, match_doc)

    check_player_match_relation(team_one_player_docs, match_doc)
    check_player_match_relation(team_two_player_docs, match_doc)


def check_team_match_relation(team_doc, match_doc):
    team_id = get_doc_id(team_doc)
    match_id = get_doc_id(match_doc)
    if team_id not in app.db.matches.find_one(match_id):
        app.db.matches.update_one({'_id': match_id}, {'$addToSet': {'teams_id': team_id}})
    if match_id not in app.db.teams.find_one(team_id):
        app.db.teams.update_one({'_id': team_id}, {'$addToSet': {'matches': match_id}})


def get_doc_id(doc):
    return doc.inserted_id if type(doc) is insert_one_res else doc['_id']


def check_player_team_relation(player_docs, team_doc):
    team_id = get_doc_id(team_doc)
    for player in player_docs:
        # player_id = player.inserted_id if type(player) is insert_one_res else player['_id']
        player_id = get_doc_id(player)
        if team_id not in app.db.players.find_one(player_id)['teams_id']:
            app.db.players.update_one({'_id': player_id}, {'$addToSet': {'teams_id': team_id}})
        if player_id not in app.db.teams.find_one(team_id):
            app.db.teams.update_one({'_id': team_id}, {'$addToSet': {'roster': player_id}})


def check_player_match_relation(player_docs, match_doc):
    match_id = get_doc_id(match_doc)
    for player in player_docs:
        # player_id = player.inserted_id if type(player) is insert_one_res else player['_id']
        player_id = get_doc_id(player)
        if match_id not in app.db.players.find_one(player_id):
            app.db.players.update_one({'_id': player_id}, {'$addToSet': {'matches': match_id}})


def create_player_docs(players_data):
    player_docs = []

    for key in list(players_data.keys()):
        group = players_data[key]
        if group:
            for player in group:
                player_name = player[list(player.keys())[0]]
                db_player = app.db.players.find_one({'name': player_name})
                if db_player:
                    player_docs.append(db_player)
                else:
                    new_player = Player(name=player_name, age=None, nationality=None, jersey_num=None)
                    player_docs.append(app.db.players.insert_one(new_player.to_mongo()))

    return player_docs


def create_team_doc(team_data):
    data_keys = list(team_data.keys())
    team_name = team_data[data_keys[0]]
    db_team = app.db.teams.find_one({'name': team_name})
    if not db_team:
        return app.db.teams.insert_one({'name': team_name})
    else:
        return db_team


def create_match_doc(comp_data):
    data_keys = list(comp_data.keys())
    name = comp_data[data_keys[0]]
    year = comp_data[data_keys[1]]
    round = comp_data[data_keys[2]]
    fixture = int(comp_data[data_keys[3]])
    db_matches = list(app.db.matches.find({'competition': name, 'year': year, 'round': round, 'fixture': fixture}))
    if len(db_matches) == 0:
        match = Match(name, year, round, fixture)
        return app.db.matches.insert_one(match.to_mongo())
    elif len(db_matches) >= 1:
        return db_matches[0]
