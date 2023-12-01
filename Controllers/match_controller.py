from mongoengine.errors import DoesNotExist


# fetching match details
class MatchController:
    def __init__(self, db):
        self.db = db
    def fetch_match_details(self,match_id):
        try:
            # Try to find a match with the given ID
            match = self.db.matches.find_one({'_id': match_id})

            return match

        except DoesNotExist:
            # If match not found, return an error message
            return {'error': 'Match not found'}
