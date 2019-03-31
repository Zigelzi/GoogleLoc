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
    session_drive = 0.0
    in_vehicle = 'IN_VEHICLE'

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

    '''
    Enumerate the activity_list and then compare the previous and current row.
    If the activity value changes from something to IN_VEHICLE then start driving session and start adding up the
    total distance driven during the session to session_drive variable.
    
    When activity type changes from IN_VEHICLE to something else, stop the driving session and reset the total drive. 
    '''
    for index, item in enumerate(activity_list):
        #print('-' * 169)

        if index > 0:

            #print(f'Previous row: {activity_list[index - 1]}')
            #print(f'Activity type: {activity_list[index - 1][3][0]["type"]}')
            #prev_coords = (activity_list[index - 1][1], activity_list[index - 1][2])
            #current_coords = (activity_list[index][1], activity_list[index][2])
            #distance = round(geodesic(prev_coords, current_coords).km, 2)
            #print(f'Distance moved: {distance} km')

            if (activity_list[index - 1][3][0]["type"] != in_vehicle) and (activity_list[index][3][0]["type"] == in_vehicle):
                drive_session = True
                print(f'\nPrevious row: {activity_list[index-1]}')
                print(f'Current row: {activity_list[index]}')
                print('Driving session has started\n')

            if (activity_list[index - 1][3][0]["type"] == in_vehicle) and (activity_list[index][3][0]["type"] != in_vehicle):
                drive_session = False
                print(f'\nPrevious row: {activity_list[index - 1]}')
                print(f'Current row: {activity_list[index]}')
                print('Driving session has ended\n')


        #print(f'Activity type: {activity_list[index][3][0]["type"]}')


        if drive_session:
            prev_coords = (activity_list[index - 1][1], activity_list[index - 1][2])
            current_coords = (activity_list[index][1], activity_list[index][2])
            distance = geodesic(prev_coords, current_coords).km
            session_drive += distance
            session_drive = round(session_drive,2)
            print(f'Total drive currently: {session_drive} km')

        if not drive_session:
            session_drive = 0.0

        #if index < (len(activity_list) - 1):
        #   print(f'\nNext row: {activity_list[index + 1]}')
        #print('-' * 169 + '\n')

    print(f'Total data points: {data_total}')
    print(f'Data points including activity: {data_activity}')

read_points()