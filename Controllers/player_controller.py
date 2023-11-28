import json
import traceback

from bson import ObjectId

import functions as fc
from htmlcodes import *
from models.player import Player, PlayerTeam, Stats, Goal
from models.short_report import shortReport


class PlayerController:
    def __init__(self, db):
        self.db = db

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
