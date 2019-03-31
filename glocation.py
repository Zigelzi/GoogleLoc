import json
from datetime import datetime
from collections import namedtuple
from geopy.distance import geodesic

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

'''
Get the Google Location history JSON dump and read its contents. Then parse the rows and add data point to point_list
if it contains the 'activity' information.

Activity information is used to determine when user is driving with car and that drive is used to analyze distances
'''
def read_points():
    data_total = 0  # Total amount of data points in the log
    data_activity = 0  # Amount of data points containing 'activity' details
    activity_list = []  # List of items in data with 'activity' details
    drive_session = False
    total_drive = 0.0

    with open('location_history.json') as f:
        data = json.load(f)

    '''
    Loop through all the items in JSON file, count total data points, data points containing 'activity' and append those
    first to own array (point_list) and then to whole array (activity_list)
    '''
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

    for index, item in enumerate(activity_list):
        print('-' * 169)

        if index > 0:

            print(f'Previous line: {activity_list[index - 1]}')
            print(f'Activity type: {activity_list[index - 1][3][0]["type"]}')
            prev_coords = (activity_list[index - 1][1], activity_list[index - 1][2])
            current_coords = (activity_list[index][1], activity_list[index][2])
            distance = round(geodesic(prev_coords, current_coords).km, 2)
            #print(f'\nPrevious latitude: {activity_list[index - 1][1]}')
            #print(f'Previous longitude: {activity_list[index - 1][2]}')
            #print(f'\nPrevious coordinates: {prev_coords}')
            #print(f'Current coordinates: {current_coords}')
            print(f'Distance moved: {distance} km')

            if (activity_list[index - 1][3][0]["type"] != 'IN_VEHICLE') and (activity_list[index][3][0]["type"] == 'IN_VEHICLE'):
                drive_session = True
                print('Driving session has started')

            if (activity_list[index - 1][3][0]["type"] == 'IN_VEHICLE') and (activity_list[index][3][0]["type"] != 'IN_VEHICLE'):
                drive_session = False
                print('Driving session has ended')


            #print(f'\nCurrent latitude: {activity_list[index][1]}')
            #print(f'Current longitude: {activity_list[index][2]}')

        print(f'\nCurrent row{activity_list[index]}')
        print(f'Activity type: {activity_list[index][3][0]["type"]}')

        if drive_session:
            prev_coords = (activity_list[index - 1][1], activity_list[index - 1][2])
            current_coords = (activity_list[index][1], activity_list[index][2])
            distance = round(geodesic(prev_coords, current_coords).km, 2)
            total_drive += distance

            print(f'Total drive currently: {total_drive} km')

        if not drive_session:
            total_drive = 0.0



        if index < (len(activity_list) - 1):
            print(f'\nNext row: {activity_list[index + 1]}')
        print('-' * 169 + '\n')

    print(f'Total data points: {data_total}')
    print(f'Data points including activity: {data_activity}')



points = yield_points()
point1 = next(points)
read_points()