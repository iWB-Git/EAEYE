import json
import traceback

from bson import ObjectId

import functions as fc
from htmlcodes import *
from models.short_report import shortReport


class PlayerController:
    def __init__(self, db):
        self.db = db


    def check_for_duplicate_player(self, name, dob, jersey_num):

        db_players = list(self.db.players.find({'name': name}))
        print(db_players)
        for player in db_players:
            if player['dob'] == dob:
                if player['jersey_num'] == jersey_num:
                    return True
        return False

    def delete_player(self, player_id):
        try:
            # check for the player's document in the database, return bad request code if so
            player_id = fc.return_oid(player_id)
            db_player = self.db.players.find_one({'_id': player_id})
            if not db_player:
                return fc.edit_html_desc(
                    ERROR_400,
                    'Player not found in database; please check your ID string and try again'
                )

            # check for duplicate entries in the database
            # for a player check if they have the same name and dob, and a unique id from the given id
            dupes = list(
                self.db.players.find(
                    {
                        'name': db_player['name'],
                        'dob': db_player['dob'],
                        '_id': {'$ne': player_id}
                    })
            )

            # if any duplicates exist return a 400 error and append the duplicate documents in question for review
            if dupes:
                return fc.append_data(
                    dupes,
                    fc.edit_html_desc(
                        ERROR_400,
                        'Duplicate entries exist in database; please review these before continuing'
                    )
                )

            # check the teams collection for any teams whose roster contain the given player's id
            id_pairs = list(self.db.teams.find({'roster': player_id}, {'_id': 1}))

            # generate a list of strictly the ObjectId strings, as opposed to key-value pairs of {'_id': *id_string*}
            team_ids = []
            for pair in id_pairs:
                team_ids.append(pair['_id'])

            # remove the player's id from all the teams identified above
            self.db.teams.update_many(
                {'_id': {'$in': team_ids}},
                {'$pull': {'roster': player_id}}
            )

            # delete the player document from the database
            self.db.players.delete_one({'_id': player_id})
            return SUCCESS_200
        except Exception as e:
            fc.print_and_return_error(e)

    def insert_player(self, request_data):
        try:
            player_data = json.loads(request_data)
            # player_data = TEST_JSON_PLAYER

            name = player_data['names'].strip().title()
            nationality = player_data['nationality']
            dob = player_data['dob']
            position = player_data['position']
            jersey_num = player_data['jersey_num']
            supporting_file = player_data['supporting_file']
            reg_date = player_data['reg_date']

            if self.check_for_duplicate_player(name=name, dob=dob, jersey_num=jersey_num):
                return fc.edit_html_desc(SUCCESS_200,
                                         'This player already exists in the database. Please use move player instead')

            db_team = self.db.teams.find_one({'_id': ObjectId(player_data['team_id'])})

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

            db_player = self.db.players.insert_one(new_player.to_mongo())
            self.db.teams.update_one({'_id': db_team['_id']}, {'$addToSet': {'roster': db_player.inserted_id}})

            return SUCCESS_201
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            return fc.edit_html_desc(ERROR_400, str(e))

    def move_player(self, request_data):
        try:

            # load json data into dict
            data = json.loads(request_data)

            # check type of player_id to ensure it's stored as an ObjectId, then query the db for that player
            # if no player exists return immediately indicating the missing player
            player_id = data['player_id'] if type(data['player_id']) is ObjectId else ObjectId(data['player_id'])
            db_player = self.db.players.find_one({'_id': player_id})
            if not db_player:
                return fc.edit_html_desc(ERROR_404, 'ID not found in players collection. Check your OID and try again.')

            # check if player has a team they are being moved from. if yes, update the player's team list and update
            # the team's roster. if not, do nothing and move on to adding the new team and updating its roster
            if data['old_team_id'] == '':
                pass
            else:
                old_team_id = data['old_team_id'] if type(data['old_team_id']) is ObjectId else ObjectId(
                    data['old_team_id'])
                self.db.players.update_one({'_id': player_id, 'teams.team_id': old_team_id},
                                           {'$set': {'teams.$.on_team': False}})
                self.db.teams.update_one({'_id': old_team_id}, {'$pull': {'roster': player_id}})

            new_team_id = data['new_team_id'] if type(data['new_team_id']) is ObjectId else ObjectId(
                data['new_team_id'])
            reg_date = data['reg_date']

            # create new PlayerTeam embedded doc
            new_team = PlayerTeam(team_id=new_team_id, reg_date=reg_date, on_team=True)

            # update the db as follows:
            # 1. update player's team list to have the new team, and flip the old team's 'on_team' flag to false
            # 2. add the player's id to his new team's roster
            # 3. remove the player's id from his old team
            self.db.players.update_one({'_id': player_id}, {'$addToSet': {'teams': new_team.to_mongo()}})
            self.db.teams.update_one({'_id': new_team_id}, {'$addToSet': {'roster': player_id}})
            print(self.db.players.find_one({'_id': player_id}))

            # return the updated player document to front end
            return fc.append_data(self.db.players.find_one({'_id': player_id}), SUCCESS_200)


        except KeyError as e:
            print('request.data :: ' + str(request_data))
            print('data :: ' + str(data))
            return fc.edit_html_desc(fc.append_data(data, ERROR_400), 'Missing ID in HTML request.\nError: ' + str(e))

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
    # function takes an _id as input

    # fetching player details
    def fetch_player_details(self, player_id):
        try:
            # Try to find player with the given ID
            player = self.db.players.find_one({'_id': player_id})
            # Return the extracted details
            print(player)
            return player

        except DoesNotExist:
            # If player not found, return an error message
            return {'error': 'Player not found'}

    # def add_report_to_player(self, player_id, report_id):
    #     # Fetch the player document
    #     print(report_id)
    #     player = self.db.players.find_one({"_id": fc.return_oid(player_id)})
    #     sr = shortReport(report_id=report_id)
    #
    #     if player:
    #         if 'short_reports' in player:
    #             psr = player['short_reports']
    #             # Append the report to the player's list of short_reports
    #             # goal = Goal(minute=int(goal_mins[i]), match_id=match_id)
    #             psr.append(sr.to_mongo())
    #         else:
    #             psr = sr.to_mongo()
    #
    #         # Update the player document in the database
    #         # self.db.players.update_one(
    #         #     {'_id': player['_id']},
    #         #     {'$set': {'short_reports': psr}}
    #         # )
    #         sr_data = sr.to_mongo()
    #         print(sr_data)
    #         self.db.players.update_one({'_id': fc.return_oid(player_id)},
    #                               {
    #                                   '$set': {'short_reports': psr}
    #                               })
    #
    #         print(f"Report {report_id} added to Player {player_id}")
    #     else:
    #         print(f"No player found with player_id {player_id}")

