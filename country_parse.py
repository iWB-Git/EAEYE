import csv
from models.country import Country
import app


def upload_countries():
    countries = []
    filename = 'static/fifa_nationalities.csv'
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            app.db.countries.insert_one(Country(name=row[0]).to_mongo())
