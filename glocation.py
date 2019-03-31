import json
from datetime import datetime
from collections import namedtuple

Point = namedtuple('Point', 'latitude, longitude, datetime, activity')


def yield_points():
    with open('location_history.json') as f:
        data = json.load(f)

    for point in data['locations']:
        yield Point(
            point['latitudeE7'] / 10 ** 7,
            point['longitudeE7'] / 10 ** 7,
            datetime.fromtimestamp(int(point['timestampMs']) / 1000),
            point['activity'][0]['activity']
        )

def read_points():
    data_total = 0
    data_activity = 0
    road = 0
    foot = 0
    other = 0
    activity_list = []
    with open('location_history.json') as f:
        data = json.load(f)

    for point in data['locations']:
        data_total += 1
        point_list = []
        if 'activity' in point:
            point_list.append(datetime.fromtimestamp(int(point['timestampMs']) / 1000))
            point_list.append(point['latitudeE7'] / 10 ** 7)
            point_list.append(point['longitudeE7'] / 10 ** 7)
            point_list.append(point['activity'][0]['activity'][:2])
            data_activity += 1
            activity_list.append(point_list)


    print(f'Total data points: {data_total}')
    print(f'Data points including activity: {data_activity}')
    for i in activity_list:
        #print(i[2][0]['type'])
        if i[3][0]['type'] == 'IN_VEHICLE':
            print('-'*169)
            print(i)
            print('-'*169+'\n')



points = yield_points()
point1 = next(points)
read_points()