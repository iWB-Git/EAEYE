import csv
from models.body import Body
import app


def upload_countries():
    filename = 'static/fifa_nationalities.csv'
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if app.db.bodies.find_one({'name': row[0]}):
                continue
            app.db.bodies.insert_one(Body(name=row[0]).to_mongo())
