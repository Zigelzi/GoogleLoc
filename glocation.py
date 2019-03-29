import json
from datetime import datetime
from collections import namedtuple

Point = namedtuple('Point', 'latitude, longitude, datetime')

def read_points():
    with open('location_history.json') as f:
        data = json.load(f)

    for point in data['locations']:
        yield Point(
            point['latitudeE7'] / 10 ** 7,
            point['longitudeE7'] / 10 ** 7,
            datetime.fromtimestamp(int(point['timestampMs']) / 1000)
        )

points = read_points()