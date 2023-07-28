# from app import db
from models.match import Match
from models.competition import Competition


def split_match_data(match_data):

    match_data_keys = list(match_data.keys())
    team_one_data = match_data[match_data_keys[0]]
    team_two_data = match_data[match_data_keys[1]]
    comp_data = match_data[match_data_keys[2]]

    team_one_data_keys = list(team_one_data.keys())
    team_two_data_keys = list(team_two_data.keys())
    team_one_players = team_one_data[team_one_data_keys[0]]
    team_two_players = team_two_data[team_two_data_keys[0]]

    match_info = parse_comp_data(comp_data)

    # COMP DATA KEYS
    # 0: competition name: 'Piston Cup'
    # 1: year: 2005
    # 2: round: 2
    # 3: fixture: 12


def parse_comp_data(comp_data):
    data_keys = list(comp_data.keys())
    comp_name = comp_data[data_keys[0]]
    comp_year = comp_data[data_keys[1]]
    comp_round = comp_data[data_keys[2]]
    comp_fixture = comp_data[data_keys[3]]
    match = Match(comp_name, comp_year, comp_round, comp_fixture)
    return match
