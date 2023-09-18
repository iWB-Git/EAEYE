from flask import Flask, jsonify, request
from flask_cors import CORS
from statsbombpy import sb

app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app

@app.route('/api/competitions', methods=['GET'])
def get_competitions():
    competitions_df = sb.competitions()
    competitions_list = competitions_df.to_dict(orient='records')
    return jsonify(competitions_list)

@app.route('/api/matches', methods=['GET'])
def get_matches():
    competition_id = request.args.get('competition_id')
    season_id = request.args.get('season_id')
    
    # Fetch matches for the specified competition and season
    matches_df = sb.matches(competition_id=competition_id, season_id=season_id)
    
    # Convert the DataFrame to a list of dictionaries
    matches_list = matches_df.to_dict(orient='records')
    
    # Return the list of matches as JSON
    return jsonify(matches_list)

if __name__ == '__main__':
    app.run(debug=True)
