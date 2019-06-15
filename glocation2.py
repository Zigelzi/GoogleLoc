import json
from datetime import datetime
from geopy.distance import geodesic
from matplotlib import pyplot as plt


def read_points():
    data_total = 0  # Total amount of data points in the log
    data_activity = 0
    travel_list = []
    speed_list = []
    date_list = []
    session_drive = 0.0

    with open('location_history_small.json') as f:
        data = json.load(f)

    '''
    Loop through all the items in JSON file, count total data points, data points containing 'activity' and append those
    first to own array (travel_list) and then to whole array (travel_list)
    '''

    for point in data['locations']:
        data_total += 1
        travel_dict = {}
        if 'activity' in point:
            travel_dict['datetime'] = datetime.fromtimestamp(int(point['timestampMs']) / 1000)
            travel_dict['lat'] = point['latitudeE7'] / 10 ** 7
            travel_dict['long'] = point['longitudeE7'] / 10 ** 7
            travel_dict['activity'] = point['activity'][0]['activity'][:2]
            data_activity += 1
            travel_list.append(travel_dict)
        else:
            travel_dict['datetime'] = datetime.fromtimestamp(int(point['timestampMs']) / 1000)
            travel_dict['lat'] = point['latitudeE7'] / 10 ** 7
            travel_dict['long'] = point['longitudeE7'] / 10 ** 7
            travel_list.append(travel_dict)

    for index, item in enumerate(travel_list):
        if index > 0:
            prev_coords = (travel_list[index - 1]['lat'], travel_list[index - 1]['long'])
            current_coords = (travel_list[index]['lat'], travel_list[index]['long'])

            # Take dates from current and previous row and calculate the difference
            travel_time = travel_list[index]['datetime'] - travel_list[index - 1]['datetime']
            distance = round(geodesic(prev_coords, current_coords).km, 2)
            speed = round(distance / (travel_time.total_seconds() / 3600), 2)
            date_list.append(travel_list[index]['datetime'])
            speed_list.append(speed)
            session_drive += distance
            session_drive = round(session_drive, 2)
            #print(travel_list[index])
            #if speed > 1:

            #print(travel_list[index]['datetime'].date())
            # TODO: Complete the plotting of the speed with matplotlib pyplot
            if 'activity' in travel_list[index]:
                print(
                    f'Total drive currently: {session_drive} km | Current drive {distance} km | Travel time: {travel_time} | Speed: {speed} km/h | Activity {travel_list[index]["activity"]}')
            else:
                print(f'Total drive currently: {session_drive} km | Current drive {distance} km | Travel time: {travel_time} | Speed: {speed} km/h')


    print(speed_list)
    pyplot.plot(speed_list)
    pyplot.show()


read_points()