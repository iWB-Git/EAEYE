from mongoengine.errors import DoesNotExist


# fetching match details
def fetch_match_details(match_id, db):
    try:
        # Try to find a match with the given ID
        match = db.matches.find_one({'_id': match_id})

        return match

    except DoesNotExist:
        # If match not found, return an error message
        return {'error': 'Match not found'}
