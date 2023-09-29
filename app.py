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
FIXTURES_CSV_JSON = {
  "competition_name": "Test Competition PP",
  "competition_year": "2023/24",
  "rounds": 30,
  "round_data": [
    {
      "round": 1,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Tuesday 15/08/2023",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 2,
          "Date": "Tuesday 15/08/2023",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Tuesday 15/08/2023",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Wednesday 16/08/2023",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 5,
          "Date": "Wednesday 16/08/2023",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 6,
          "Date": "Thursday 17/08/2023",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Tuesday 22/08/2023",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Wednesday 23/08/2023",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        }
      ]
    },
    {
      "round": 2,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Saturday 19/08/2023",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 2,
          "Date": "Saturday 19/08/2023",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Sunday 20/08/2023",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Sunday 20/08/2023",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Monday 21/08/2023",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 6,
          "Date": "Monday 28/08/2023",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 7,
          "Date": "Tuesday 29/08/2023",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 8,
          "Date": "Thursday 31/08/2023",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        }
      ]
    },
    {
      "round": 3,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 15/09/2023",
          "HomeTeam": "KMC FC",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Friday 15/09/2023",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 3,
          "Date": "Friday 15/09/2023",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Saturday 16/09/2023",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Saturday 16/09/2023",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 6,
          "Date": "Saturday 16/09/2023",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 7,
          "Date": "Saturday 16/09/2023",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 8,
          "Date": "Saturday 16/09/2023",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        }
      ]
    },
    {
      "round": 4,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 29/09/2023",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Friday 29/09/2023",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Saturday 30/09/2023",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Saturday 30/09/2023",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Tuesday 03/10/2023",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Tuesday 03/10/2023",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Wednesday 04/10/2023",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 8,
          "Date": "Thursday 05/10/2023",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        }
      ]
    },
    {
      "round": 5,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Thursday 19/10/2023",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Friday 20/10/2023",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Friday 20/10/2023",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Friday 20/10/2023",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Saturday 21/10/2023",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 22/10/2023",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 22/10/2023",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 22/10/2023",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        }
      ]
    },
    {
      "round": 6,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Monday 23/10/2023",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Tuesday 24/10/2023",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Wednesday 25/10/2023",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Wednesday 25/10/2023",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 5,
          "Date": "Wednesday 25/10/2023",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 6,
          "Date": "Wednesday 25/10/2023",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Thursday 26/10/2023",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 8,
          "Date": "Thursday 26/10/2023",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        }
      ]
    },
    {
      "round": 7,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Saturday 28/10/2023",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Saturday 28/10/2023",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 3,
          "Date": "Saturday 28/10/2023",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Sunday 29/10/2023",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 5,
          "Date": "Sunday 29/10/2023",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 29/10/2023",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 29/10/2023",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 29/10/2023",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        }
      ]
    },
    {
      "round": 8,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Tuesday 31/10/2023",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Wednesday 01/11/2023",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Wednesday 01/11/2023",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Wednesday 01/11/2023",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Thursday 02/11/2023",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Thursday 02/11/2023",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 7,
          "Date": "Thursday 02/11/2023",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 05/11/2023",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        }
      ]
    },
    {
      "round": 9,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Saturday 04/11/2023",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Sunday 05/11/2023",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Sunday 05/11/2023",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Monday 06/11/2023",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 5,
          "Date": "Monday 06/11/2023",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 6,
          "Date": "Tuesday 07/11/2023",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Saturday 11/11/2023",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Saturday 11/11/2023",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        }
      ]
    },
    {
      "round": 10,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 24/11/2023",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Friday 24/11/2023",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Saturday 25/11/2023",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 4,
          "Date": "Saturday 25/11/2023",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Saturday 25/11/2023",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 6,
          "Date": "Saturday 25/11/2023",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 7,
          "Date": "Saturday 25/11/2023",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Saturday 25/11/2023",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        }
      ]
    },
    {
      "round": 11,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Tuesday 28/11/2023",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Tuesday 28/11/2023",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Tuesday 28/11/2023",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 4,
          "Date": "Wednesday 29/11/2023",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Wednesday 29/11/2023",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Wednesday 29/11/2023",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Thursday 30/11/2023",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Thursday 30/11/2023",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        }
      ]
    },
    {
      "round": 12,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Sunday 03/12/2023",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 2,
          "Date": "Sunday 03/12/2023",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Sunday 03/12/2023",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Monday 04/12/2023",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 5,
          "Date": "Monday 04/12/2023",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 6,
          "Date": "Monday 04/12/2023",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 7,
          "Date": "Monday 04/12/2023",
          "HomeTeam": "Singida BS",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Monday 04/12/2023",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        }
      ]
    },
    {
      "round": 13,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Saturday 09/12/2023",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 2,
          "Date": "Saturday 09/12/2023",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Sunday 10/12/2023",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Sunday 10/12/2023",
          "HomeTeam": "Singida BS",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Sunday 10/12/2023",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 10/12/2023",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 10/12/2023",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 10/12/2023",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        }
      ]
    },
    {
      "round": 14,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Tuesday 19/12/2023",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Wednesday 20/12/2023",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Wednesday 20/12/2023",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Thursday 21/12/2023",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Thursday 21/12/2023",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 6,
          "Date": "Thursday 21/12/2023",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 7,
          "Date": "Thursday 21/12/2023",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Thursday 21/12/2023",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        }
      ]
    },
    {
      "round": 15,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Tuesday 26/12/2023",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Tuesday 26/12/2023",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Tuesday 26/12/2023",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Wednesday 27/12/2023",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Wednesday 27/12/2023",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Thursday 28/12/2023",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 7,
          "Date": "Thursday 28/12/2023",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Thursday 28/12/2023",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        }
      ]
    },
    {
      "round": 16,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Saturday 30/12/2023",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 2,
          "Date": "Saturday 30/12/2023",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Sunday 31/12/2023",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Sunday 31/12/2023",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 5,
          "Date": "Sunday 31/12/2023",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 6,
          "Date": "Monday 01/01/2024",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Monday 01/01/2024",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Tuesday 02/01/2024",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        }
      ]
    },
    {
      "round": 17,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 16/02/2024",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Friday 16/02/2024",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 3,
          "Date": "Friday 16/02/2024",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Saturday 17/02/2024",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Saturday 17/02/2024",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 18/02/2024",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 18/02/2024",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 18/02/2024",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        }
      ]
    },
    {
      "round": 18,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 23/02/2024",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Friday 23/02/2024",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Saturday 24/02/2024",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Saturday 24/02/2024",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Sunday 25/02/2024",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 25/02/2024",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 25/02/2024",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 25/02/2024",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        }
      ]
    },
    {
      "round": 19,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Tuesday 27/02/2024",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Tuesday 27/02/2024",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 3,
          "Date": "Wednesday 28/02/2024",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 4,
          "Date": "Wednesday 28/02/2024",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Wednesday 28/02/2024",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 6,
          "Date": "Thursday 29/02/2024",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 7,
          "Date": "Thursday 29/02/2024",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Thursday 29/02/2024",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        }
      ]
    },
    {
      "round": 20,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Sunday 03/03/2024",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 2,
          "Date": "Sunday 03/03/2024",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Sunday 03/03/2024",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Monday 04/03/2024",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 5,
          "Date": "Monday 04/03/2024",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 6,
          "Date": "Monday 04/03/2024",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 7,
          "Date": "Monday 04/03/2024",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 8,
          "Date": "Monday 04/03/2024",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        }
      ]
    },
    {
      "round": 21,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 29/03/2024",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Saturday 30/03/2024",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Saturday 30/03/2024",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Sunday 31/03/2024",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 5,
          "Date": "Sunday 31/03/2024",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 31/03/2024",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 31/03/2024",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 31/03/2024",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        }
      ]
    },
    {
      "round": 22,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 05/04/2024",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 2,
          "Date": "Saturday 06/04/2024",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Sunday 07/04/2024",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 4,
          "Date": "Sunday 07/04/2024",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Monday 08/04/2024",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 6,
          "Date": "Monday 08/04/2024",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Monday 08/04/2024",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Monday 08/04/2024",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        }
      ]
    },
    {
      "round": 23,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 12/04/2024",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 2,
          "Date": "Friday 12/04/2024",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Friday 12/04/2024",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 4,
          "Date": "Saturday 13/04/2024",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 5,
          "Date": "Sunday 14/04/2024",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 14/04/2024",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 14/04/2024",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Monday 15/04/2024",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        }
      ]
    },
    {
      "round": 24,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 19/04/2024",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Saturday 20/04/2024",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 3,
          "Date": "Saturday 20/04/2024",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Sunday 21/04/2024",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Sunday 21/04/2024",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 21/04/2024",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 21/04/2024",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 21/04/2024",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        }
      ]
    },
    {
      "round": 25,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 26/04/2024",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Saturday 27/04/2024",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 3,
          "Date": "Sunday 28/04/2024",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Sunday 28/04/2024",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 5,
          "Date": "Sunday 28/04/2024",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 28/04/2024",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 28/04/2024",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 28/04/2024",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        }
      ]
    },
    {
      "round": 26,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Tuesday 30/04/2024",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 2,
          "Date": "Wednesday 01/05/2024",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Wednesday 01/05/2024",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 4,
          "Date": "Wednesday 01/05/2024",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        },
        {
          "MatchUp": 5,
          "Date": "Wednesday 01/05/2024",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Thursday 02/05/2024",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 7,
          "Date": "Thursday 02/05/2024",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Thursday 02/05/2024",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        }
      ]
    },
    {
      "round": 27,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 10/05/2024",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Saturday 11/05/2024",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 3,
          "Date": "Saturday 11/05/2024",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Saturday 11/05/2024",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Sunday 12/05/2024",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Sunday 12/05/2024",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Sunday 12/05/2024",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Sunday 12/05/2024",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Simba Sports Club",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        }
      ]
    },
    {
      "round": 28,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Friday 17/05/2024",
          "HomeTeam": "Kitayosa FC",
          "AwayTeam": "Ihefu Sports Club",
          "FullMatchURL": "",
          "Venue": "Ali Hassan Mwinyi"
        },
        {
          "MatchUp": 2,
          "Date": "Friday 17/05/2024",
          "HomeTeam": "Kagera Sugar Football Club",
          "AwayTeam": "Coastal Union SC",
          "FullMatchURL": "",
          "Venue": "Kaitaba Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Saturday 18/05/2024",
          "HomeTeam": "Tanzania Prisons Football Club",
          "AwayTeam": "Mashujaa FC",
          "FullMatchURL": "",
          "Venue": "Sokoine Stadium"
        },
        {
          "MatchUp": 4,
          "Date": "Sunday 19/05/2024",
          "HomeTeam": "Mtibwa Sugar Sports Club",
          "AwayTeam": "Namungo FC",
          "FullMatchURL": "",
          "Venue": "Manungu Stadium"
        },
        {
          "MatchUp": 5,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Dodoma Jiji FC",
          "AwayTeam": "Young Africans Sports Club",
          "FullMatchURL": "",
          "Venue": "Jamhuri Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "JKT Tanzania Sports Club",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Black Rhino Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 8,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "KMC FC",
          "AwayTeam": "Singida BS",
          "FullMatchURL": "",
          "Venue": "Uhuru Stadium"
        }
      ]
    },
    {
      "round": 29,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 2,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 3,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 4,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 5,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 6,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Benjamin Mkapa"
        },
        {
          "MatchUp": 7,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Geita Gold FC",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Monday 20/05/2024",
          "HomeTeam": "Azam Football Club",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Azam Complex"
        }
      ]
    },
    {
      "round": 30,
      "round_data": [
        {
          "MatchUp": 1,
          "Date": "Wednesday 29/05/2024",
          "HomeTeam": "Simba Sports Club",
          "AwayTeam": "JKT Tanzania Sports Club",
          "FullMatchURL": "",
          "Venue": "TBC"
        },
        {
          "MatchUp": 2,
          "Date": "Wednesday 29/05/2024",
          "HomeTeam": "Coastal Union SC",
          "AwayTeam": "KMC FC",
          "FullMatchURL": "",
          "Venue": "Mkwakwani Stadium"
        },
        {
          "MatchUp": 3,
          "Date": "Wednesday 29/05/2024",
          "HomeTeam": "Mashujaa FC",
          "AwayTeam": "Dodoma Jiji FC",
          "FullMatchURL": "",
          "Venue": "Lake Tanganyika"
        },
        {
          "MatchUp": 4,
          "Date": "Wednesday 29/05/2024",
          "HomeTeam": "Ihefu Sports Club",
          "AwayTeam": "Mtibwa Sugar Sports Club",
          "FullMatchURL": "",
          "Venue": "Highland Estates"
        },
        {
          "MatchUp": 5,
          "Date": "Wednesday 29/05/2024",
          "HomeTeam": "Young Africans Sports Club",
          "AwayTeam": "Tanzania Prisons Football Club",
          "FullMatchURL": "",
          "Venue": "TBC"
        },
        {
          "MatchUp": 6,
          "Date": "Wednesday 29/05/2024",
          "HomeTeam": "Namungo FC",
          "AwayTeam": "Kitayosa FC",
          "FullMatchURL": "",
          "Venue": "Majaliwa Stadium"
        },
        {
          "MatchUp": 7,
          "Date": "Wednesday 29/05/2024",
          "HomeTeam": "Geita Gold FC",
          "AwayTeam": "Azam Football Club",
          "FullMatchURL": "",
          "Venue": "Nyankumbu Stadium"
        },
        {
          "MatchUp": 8,
          "Date": "Wednesday 29/05/2024",
          "HomeTeam": "Singida BS",
          "AwayTeam": "Kagera Sugar Football Club",
          "FullMatchURL": "",
          "Venue": "Liti Stadium"
        }
      ]
    }
  ]
}
PLAYERS_CSV_JSON = [
    {
        "team": "Enyimba",
        "player_data": [
            {
                "Team": "Enyimba",
                "Name": "Frank Boateng",
                "JerseyNo": "1",
                "DateOfBirth": "28/5/1994",
                "RegistrationDate": "28/5/1994",
                "Nationality": "Ghana"
            },
            {
                "Team": "Enyimba",
                "Name": "Bilal Yakubu",
                "JerseyNo": "2",
                "DateOfBirth": "12/12/2000",
                "RegistrationDate": "12/12/2000",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Ubong Ini Edem",
                "JerseyNo": "3",
                "DateOfBirth": "10/9/2003",
                "RegistrationDate": "10/9/2003",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Sylvester Desmond Ojietefian",
                "JerseyNo": "4",
                "DateOfBirth": "20/3/2004",
                "RegistrationDate": "20/3/2004",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Happy Ekwutoziam Eze",
                "JerseyNo": "6",
                "DateOfBirth": "27/12/2001",
                "RegistrationDate": "27/12/2001",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Joseph Saaaondo Atule",
                "JerseyNo": "7",
                "DateOfBirth": "24/12/2000",
                "RegistrationDate": "24/12/2000",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Owen Enyia George",
                "JerseyNo": "8",
                "DateOfBirth": "24/4/2004",
                "RegistrationDate": "24/4/2004",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Ikenna Toscore Uwandu",
                "JerseyNo": "9",
                "DateOfBirth": "19/10/1998",
                "RegistrationDate": "19/10/1998",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Elijah Sodiq Akanni",
                "JerseyNo": "10",
                "DateOfBirth": "22/8/2001",
                "RegistrationDate": "22/8/2001",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Chisom Sunday Okereke",
                "JerseyNo": "11",
                "DateOfBirth": "3/12/2003",
                "RegistrationDate": "3/12/2003",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Olorunleke Oluwasegun Ojo",
                "JerseyNo": "12",
                "DateOfBirth": "17/8/1995",
                "RegistrationDate": "17/8/1995",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Anthony Achu Okachi",
                "JerseyNo": "13",
                "DateOfBirth": "6/9/2000",
                "RegistrationDate": "6/9/2000",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Nelson Osahon Osoboh",
                "JerseyNo": "14",
                "DateOfBirth": "17/7/2000",
                "RegistrationDate": "17/7/2000",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Chijioke Miracle Mbaoma",
                "JerseyNo": "15",
                "DateOfBirth": "6/5/2003",
                "RegistrationDate": "6/5/2003",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Kusi Gordon Brokelyn",
                "JerseyNo": "16",
                "DateOfBirth": "19/11/2000",
                "RegistrationDate": "19/11/2000",
                "Nationality": "Ghana"
            },
            {
                "Team": "Enyimba",
                "Name": "Seth Sowah",
                "JerseyNo": "17",
                "DateOfBirth": "30/6/1995",
                "RegistrationDate": "30/6/1995",
                "Nationality": "Ghana"
            },
            {
                "Team": "Enyimba",
                "Name": "Pascal Nduka Eze",
                "JerseyNo": "18",
                "DateOfBirth": "23/3/2000",
                "RegistrationDate": "23/3/2000",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Ezekiel Chisom Ngomere",
                "JerseyNo": "19",
                "DateOfBirth": "20/11/2000",
                "RegistrationDate": "20/11/2000",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Daniel Victor Ekpo",
                "JerseyNo": "20",
                "DateOfBirth": "1/5/1996",
                "RegistrationDate": "1/5/1996",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Sabirou Bassa Djeri",
                "JerseyNo": "21",
                "DateOfBirth": "31/12/1995",
                "RegistrationDate": "31/12/1995",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Ikenna Gerald Cooper",
                "JerseyNo": "22",
                "DateOfBirth": "30/4/2002",
                "RegistrationDate": "30/4/2002",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Stephen Chekwube Chukwude",
                "JerseyNo": "23",
                "DateOfBirth": "21/10/1994",
                "RegistrationDate": "21/10/1994",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Chigozie Emmanuel Chilekwu",
                "JerseyNo": "24",
                "DateOfBirth": "4/6/1996",
                "RegistrationDate": "4/6/1996",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Somiari Orinate Alalibo",
                "JerseyNo": "25",
                "DateOfBirth": "30/11/2001",
                "RegistrationDate": "30/11/2001",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Chikamuso Okechukwu Chikamuso",
                "JerseyNo": "26",
                "DateOfBirth": "25/4/2002",
                "RegistrationDate": "25/4/2002",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Chibuike Godfrey Nwaiwu",
                "JerseyNo": "27",
                "DateOfBirth": "23/7/2003",
                "RegistrationDate": "23/7/2003",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "James Oronsaye",
                "JerseyNo": "28",
                "DateOfBirth": "25/6/2003",
                "RegistrationDate": "25/6/2003",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Imo Obot Udo",
                "JerseyNo": "29",
                "DateOfBirth": "15/12/2002",
                "RegistrationDate": "15/12/2002",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Ekene Kennedy Awazie",
                "JerseyNo": "30",
                "DateOfBirth": "1/12/1996",
                "RegistrationDate": "1/12/1996",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Tijani Kabiru",
                "JerseyNo": "31",
                "DateOfBirth": "8/8/2000",
                "RegistrationDate": "8/8/2000",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Murphy Ndukwu",
                "JerseyNo": "32",
                "DateOfBirth": "27/3/2003",
                "RegistrationDate": "27/3/2003",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Uwana Asuquo Enoh",
                "JerseyNo": "33",
                "DateOfBirth": "1/5/1999",
                "RegistrationDate": "1/5/1999",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Eriugo Peter Adiele",
                "JerseyNo": "34",
                "DateOfBirth": "12/8/2006",
                "RegistrationDate": "12/8/2006",
                "Nationality": "Nigeria"
            },
            {
                "Team": "Enyimba",
                "Name": "Henry Ozoemena Ani",
                "JerseyNo": "35",
                "DateOfBirth": "27/10/2000",
                "RegistrationDate": "27/10/2000",
                "Nationality": "Nigeria"
            }
        ]
    },
    {
        "team": "Insurance",
        "player_data": [
            {
                "Team": "Insurance",
                "Name": "David Obiazo",
                "JerseyNo": "1",
                "DateOfBirth": "21/2/2000",
                "RegistrationDate": "21/2/2000",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Jide Oluwafemi Williams",
                "JerseyNo": "3",
                "DateOfBirth": "4/4/1996",
                "RegistrationDate": "4/4/1996",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Julius Junior Emiloju",
                "JerseyNo": "4",
                "DateOfBirth": "7/5/1998",
                "RegistrationDate": "7/5/1998",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Maurice Prince",
                "JerseyNo": "6",
                "DateOfBirth": "6/12/1992",
                "RegistrationDate": "6/12/1992",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Ismail Ishak Sarki",
                "JerseyNo": "7",
                "DateOfBirth": "10/10/2002",
                "RegistrationDate": "10/10/2002",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Ogadi Okenwa",
                "JerseyNo": "9",
                "DateOfBirth": "12/3/2004",
                "RegistrationDate": "12/3/2004",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Zaidu Ayuba",
                "JerseyNo": "10",
                "DateOfBirth": "1/1/1999",
                "RegistrationDate": "1/1/1999",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Jude Ebohon",
                "JerseyNo": "11",
                "DateOfBirth": "19/6/2004",
                "RegistrationDate": "19/6/2004",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Amas Obasogie",
                "JerseyNo": "12",
                "DateOfBirth": "27/12/1999",
                "RegistrationDate": "27/12/1999",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Sunday Anyanwu",
                "JerseyNo": "14",
                "DateOfBirth": "28/8/2000",
                "RegistrationDate": "28/8/2000",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Evans Iyebi Ogbonda",
                "JerseyNo": "18",
                "DateOfBirth": "11/3/2002",
                "RegistrationDate": "11/3/2002",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Ebenezer Olaonipekun Odeyemi",
                "JerseyNo": "19",
                "DateOfBirth": "15/9/1991",
                "RegistrationDate": "15/9/1991",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Imade Osarenkhoe",
                "JerseyNo": "22",
                "DateOfBirth": "19/11/2000",
                "RegistrationDate": "19/11/2000",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Stanley Okorom",
                "JerseyNo": "23",
                "DateOfBirth": "19/11/2000",
                "RegistrationDate": "19/11/2000",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Austine Ogunye",
                "JerseyNo": "24",
                "DateOfBirth": "1/8/1997",
                "RegistrationDate": "1/8/1997",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Efe Ugiagbe Aghama",
                "JerseyNo": "25",
                "DateOfBirth": "11/6/2004",
                "RegistrationDate": "11/6/2004",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Kelly Kester Oahimije",
                "JerseyNo": "27",
                "DateOfBirth": "16/6/1992",
                "RegistrationDate": "16/6/1992",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Benjamin Tanimu",
                "JerseyNo": "28",
                "DateOfBirth": "24/7/2002",
                "RegistrationDate": "24/7/2002",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Paul Oghale Obata",
                "JerseyNo": "30",
                "DateOfBirth": "1/6/1996",
                "RegistrationDate": "1/6/1996",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Abdullahi Hussein",
                "JerseyNo": "31",
                "DateOfBirth": "6/6/2002",
                "RegistrationDate": "6/6/2002",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Koma Millions",
                "JerseyNo": "32",
                "DateOfBirth": "1/5/2004",
                "RegistrationDate": "1/5/2004",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Tamarebhifa Ezekiel Ojudigha",
                "JerseyNo": "33",
                "DateOfBirth": "9/1/2000",
                "RegistrationDate": "9/1/2000",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Vincent Augustus",
                "JerseyNo": "34",
                "DateOfBirth": "3/3/2006",
                "RegistrationDate": "3/3/2006",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Peter Emuobo Ambrose",
                "JerseyNo": "35",
                "DateOfBirth": "23/12/1995",
                "RegistrationDate": "23/12/1995",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Joshua Baba",
                "JerseyNo": "36",
                "DateOfBirth": "7/6/2004",
                "RegistrationDate": "7/6/2004",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Insurance",
                "Name": "Haruna Mohammed Abubakar",
                "JerseyNo": "37",
                "DateOfBirth": "10/1/2003",
                "RegistrationDate": "10/1/2003",
                "Nationality": "Nigerian"
            }
        ]
    },
    {
        "team": "Rivers United",
        "player_data": [
            {
                "Team": "Rivers United",
                "Name": "Abiodun Asimiyu Akande",
                "JerseyNo": "1",
                "DateOfBirth": "10/12/1993",
                "RegistrationDate": "10/12/1993",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Muyiwa Adeola Fehintola",
                "JerseyNo": "2",
                "DateOfBirth": "18/10/2000",
                "RegistrationDate": "18/10/2000",
                "Nationality": "Beninise"
            },
            {
                "Team": "Rivers United",
                "Name": "Emmanuel Ampiah",
                "JerseyNo": "3",
                "DateOfBirth": "4/4/1992",
                "RegistrationDate": "4/4/1992",
                "Nationality": "Ghanaian"
            },
            {
                "Team": "Rivers United",
                "Name": "Uche John Akubueze",
                "JerseyNo": "4",
                "DateOfBirth": "26/10/1991",
                "RegistrationDate": "26/10/1991",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Endurance Eddy Ebedebiri",
                "JerseyNo": "5",
                "DateOfBirth": "16/6/2003",
                "RegistrationDate": "16/6/2003",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Kazie Godswill Enyinnaya",
                "JerseyNo": "6",
                "DateOfBirth": "12/4/1999",
                "RegistrationDate": "12/4/1999",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Abba Suleiman",
                "JerseyNo": "7",
                "DateOfBirth": "2/1/2002",
                "RegistrationDate": "2/1/2002",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Ukeme Mitchel Williams",
                "JerseyNo": "8",
                "DateOfBirth": "12/9/1999",
                "RegistrationDate": "12/9/1999",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Mark Theo Gibson",
                "JerseyNo": "9",
                "DateOfBirth": "9/11/2004",
                "RegistrationDate": "9/11/2004",
                "Nationality": "Liberian"
            },
            {
                "Team": "Rivers United",
                "Name": "Alex Young Oyowah",
                "JerseyNo": "10",
                "DateOfBirth": "7/1/2004",
                "RegistrationDate": "7/1/2004",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Shedrack Asiegbu",
                "JerseyNo": "11",
                "DateOfBirth": "28/7/1999",
                "RegistrationDate": "28/7/1999",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Albert Robert Korvah",
                "JerseyNo": "12",
                "DateOfBirth": "2/5/1999",
                "RegistrationDate": "2/5/1999",
                "Nationality": "Liberian"
            },
            {
                "Team": "Rivers United",
                "Name": "Adekunle David Adeleke",
                "JerseyNo": "13",
                "DateOfBirth": "27/7/2002",
                "RegistrationDate": "27/7/2002",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Fatai Abdullahi Oluwadayo",
                "JerseyNo": "14",
                "DateOfBirth": "22/7/2002",
                "RegistrationDate": "22/7/2002",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Anthony Chinedu Ohaegbu",
                "JerseyNo": "15",
                "DateOfBirth": "25/4/2001",
                "RegistrationDate": "25/4/2001",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Sochima Victor Ndukauba",
                "JerseyNo": "16",
                "DateOfBirth": "8/1/1999",
                "RegistrationDate": "8/1/1999",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Farouk Mohammed",
                "JerseyNo": "17",
                "DateOfBirth": "9/7/1995",
                "RegistrationDate": "9/7/1995",
                "Nationality": "Ghanaian"
            },
            {
                "Team": "Rivers United",
                "Name": "Chiamaka Emmanuel Madu",
                "JerseyNo": "18",
                "DateOfBirth": "27/7/1996",
                "RegistrationDate": "27/7/1996",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Paul Inalegwu Odey",
                "JerseyNo": "19",
                "DateOfBirth": "26/9/2001",
                "RegistrationDate": "26/9/2001",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Joseph Onoja",
                "JerseyNo": "20",
                "DateOfBirth": "6/11/1998",
                "RegistrationDate": "6/11/1998",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Seidu Mutawakilu",
                "JerseyNo": "21",
                "DateOfBirth": "8/8/1995",
                "RegistrationDate": "8/8/1995",
                "Nationality": "Ghanaian"
            },
            {
                "Team": "Rivers United",
                "Name": "Paul Acquah",
                "JerseyNo": "23",
                "DateOfBirth": "4/5/1995",
                "RegistrationDate": "4/5/1995",
                "Nationality": "Ghanaian"
            },
            {
                "Team": "Rivers United",
                "Name": "Victor Arikpo Eteng",
                "JerseyNo": "24",
                "DateOfBirth": "8/6/1999",
                "RegistrationDate": "8/6/1999",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Augustine Okejepha",
                "JerseyNo": "25",
                "DateOfBirth": "13/4/2004",
                "RegistrationDate": "13/4/2004",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Kouassi Bernard Yao",
                "JerseyNo": "26",
                "DateOfBirth": "7/7/1994",
                "RegistrationDate": "7/7/1994",
                "Nationality": "Ivorian"
            },
            {
                "Team": "Rivers United",
                "Name": "Samuel Adom Antwi",
                "JerseyNo": "27",
                "DateOfBirth": "5/5/2000",
                "RegistrationDate": "5/5/2000",
                "Nationality": "Ghanaian"
            },
            {
                "Team": "Rivers United",
                "Name": "Nyima Nekabari Nwagua",
                "JerseyNo": "28",
                "DateOfBirth": "9/5/1993",
                "RegistrationDate": "9/5/1993",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Lukman Adefemi Abegunrin",
                "JerseyNo": "29",
                "DateOfBirth": "13/3/1994",
                "RegistrationDate": "13/3/1994",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Chibuzor Ogbodo Eze",
                "JerseyNo": "30",
                "DateOfBirth": "26/1/2000",
                "RegistrationDate": "26/1/2000",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Godswill Godstime Azeez",
                "JerseyNo": "31",
                "DateOfBirth": "2/5/2003",
                "RegistrationDate": "2/5/2003",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Precious Agu",
                "JerseyNo": "32",
                "DateOfBirth": "18/7/1999",
                "RegistrationDate": "18/7/1999",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Temple Emekayi",
                "JerseyNo": "33",
                "DateOfBirth": "5/1/1998",
                "RegistrationDate": "5/1/1998",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Osagie Onisodemuya",
                "JerseyNo": "34",
                "DateOfBirth": "20/9/2001",
                "RegistrationDate": "20/9/2001",
                "Nationality": "Nigerian"
            },
            {
                "Team": "Rivers United",
                "Name": "Deputy Ugonna Echeta",
                "JerseyNo": "35",
                "DateOfBirth": "23/12/2000",
                "RegistrationDate": "23/12/2000",
                "Nationality": "Nigerian"
            }
        ]
    }
]

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
            new_comp = Competition(name=name, teams=[])
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


@app.route('/api/v2/upload-csv/fixtures', methods=['POST'])
def upload_fixture_csv():
    try:
        # comp_id = return_oid(db.competitions.find_one({'name': data['competition_name'].strip().title()}))
        data =json.loads(request.data)
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
    # upload_fixture_csv(FIXTURES_CSV_JSON)
    # upload_players_csv(PLAYERS_CSV_JSON)
    app.debug = False
    app.run()
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
