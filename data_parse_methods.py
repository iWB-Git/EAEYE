from app import db

# TODO: clean/refactor all methods


def parse_match_data(match_data):
    match_data_keys = list(match_data.keys())
    team_one_data = match_data[match_data_keys[0]]
    team_two_data = match_data[match_data_keys[1]]
    comp_data = match_data[match_data_keys[2]]
    # print(str(comp_data))
    parse_comp_data(comp_data)
    parse_team_data(team_one_data)
    parse_team_data(team_two_data)


def parse_comp_data(comp_data):
    comp_data_keys = list(comp_data.keys())

    for key in list(comp_data.keys()):
        print(key + ': ' + comp_data[key])


def parse_team_data(team_data):
    team_data_keys = list(team_data.keys())
    # team_name = team_data[team_data_keys[0]]
    team_players = team_data[team_data_keys[1]]
    parse_player_data(team_players)


def parse_player_data(roster_data):
    for key in list(roster_data.keys()):
        if len(roster_data[key]):
            insert_player_data(roster_data[key])
        else:
            print('ERROR DURING DATA PARSE: \"app.py: parse_player_data(roster_data)\": ' + key + ' IS EMPTY')
    # roster_data_keys = list(roster_data.keys())
    # starters = roster_data[roster_data_keys[0]]
    # bench = roster_data[roster_data_keys[1]]

    # insert_player_data(starters) if len(starters) \
    #     else print('ERROR DURING DATA UPLOAD: \"app.py: parse_player_data(player_data)\": CANNOT UPLOAD EMPTY LIST\n')
    #
    # insert_player_data(bench) if len(bench) \
    #     else print('ERROR DURING DATA UPLOAD: \"app.py: parse_player_data(player_data)\": CANNOT UPLOAD EMPTY LIST\n')


def insert_player_data(players):
    for player in players:
        # for val in player:
        #     print(val)
        #     print(player[val])
        # player_keys = list(player.keys())
        for key in list(player.keys()):
            print(player[key])

    db_players = db.players
    db_players.insert_many(players)
