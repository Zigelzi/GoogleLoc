import json
from datetime import datetime
from geopy.distance import geodesic

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
    non_total_drive = 0
    session_drive = 0.0
    ev_consumption = 0.18
    speed_list = []
    high_speeds = []
    high_speed_counter = 0
    max_drives = []
    max_drive_counter = 0
    non_activity_list = []
    non_activity_points = 0
    in_vehicle = 'IN_VEHICLE'

    with open('location_history_small.json') as f:
        data = json.load(f)

    '''
    Loop through all the items in JSON file, count total data points, data points containing 'activity' and append those
    first to own array (activity_list) and then to whole array (activity_list)
    '''
    for point in data['locations']:
        data_total += 1
        activity_dict = {}
        non_activity_dict = {}
        if 'activity' in point:
            activity_dict['datetime'] = datetime.fromtimestamp(int(point['timestampMs']) / 1000)
            activity_dict['lat'] = point['latitudeE7'] / 10 ** 7
            activity_dict['long'] = point['longitudeE7'] / 10 ** 7
            activity_dict['activity'] = point['activity'][0]['activity'][:2]
            data_activity += 1
            activity_list.append(activity_dict)
        else:
            non_activity_dict['datetime'] = datetime.fromtimestamp(int(point['timestampMs']) / 1000)
            non_activity_dict['lat'] = point['latitudeE7'] / 10 ** 7
            non_activity_dict['long'] = point['longitudeE7'] / 10 ** 7
            non_activity_list.append(non_activity_dict)

    '''
    Enumerate the activity_list and then compare the previous and current row.
    If the activity value changes from something to IN_VEHICLE then start driving session and start adding up the
    total distance driven during the session to session_drive variable.
    
    When activity type changes from IN_VEHICLE to something else, stop the driving session and reset the total drive. 
    '''
    for index, item in enumerate(activity_list):
        # Check that there's previous row to compare to
        if index > 0:
            # Check if previous activity type is not IN_VEHICLE and that current activity type is IN_VEHCILE
            # Then set the drive_session to status TRUE to represent ongoing session
            if (activity_list[index - 1]['activity'][0]["type"] != in_vehicle) \
                    and (activity_list[index]['activity'][0]["type"] == in_vehicle):
                drive_session = True
                print(f'\nPrevious row: {activity_list[index-1]}')
                print(f'Current row: {activity_list[index]}')
                print('Driving session has started\n')

            # Check that previous activity type is IN_VEHICLE and that next activity type isn't IN_VEHICLE
            # Add the last change (IN_VEHICLE -> SOMETHING_ELSE) to the session_drive and then finish the session
            # Then set the status of drive_session back to FALSE to represent ended drive session
            if (activity_list[index - 1]['activity'][0]["type"] == in_vehicle) \
                    and (activity_list[index]['activity'][0]["type"] != in_vehicle):
                drive_session = False

                # Take previous and current coordinates
                prev_coords = (activity_list[index - 1]['lat'], activity_list[index - 1]['long'])
                current_coords = (activity_list[index]['lat'], activity_list[index]['long'])

                # Take dates from current and previous row and calculate the difference
                travel_time = activity_list[index]['datetime'] - activity_list[index - 1]['datetime']
                distance = round(geodesic(prev_coords, current_coords).km, 2)
                speed = round(distance / (travel_time.total_seconds() / 3600), 2)
                speed_list.append(speed)
                session_drive += distance
                session_drive = round(session_drive, 2)
                total_drive += session_drive
                energy = round(session_drive * ev_consumption, 2)
                if session_drive > 100.0:
                    max_drives.append(activity_list[index])
                    max_drive_counter += 1

                print(f'\nPrevious row: {activity_list[index - 1]}')
                print(f'Current row: {activity_list[index]}')
                if speed_list:
                    speed_avg = round(sum(speed_list) / len(speed_list), 2)
                    print(f'Average speed of the session is {speed_avg} km/h')
                    if speed_avg > 150:
                        high_speed_counter += 1
                        high_speeds.append(activity_list[index])
                print(f'ACTIVITY: Total drive currently: {session_drive} km | Current drive {distance} km | Energy used: {energy} kWh | Travel time: {travel_time} | Speed: {speed} km/h')
                print('Driving session has ended\n')


        # If the drive_session is ongoing (TRUE), then calculate distance between previous and current row coordinates
        # Add that value to total session_drive value and print them out
        if drive_session:
            # Take previous and current coordinates
            prev_coords = (activity_list[index - 1]['lat'], activity_list[index - 1]['long'])
            current_coords = (activity_list[index]['lat'], activity_list[index]['long'])

            # Take dates from current and previous row and calculate the difference
            travel_time = activity_list[index]['datetime'] - activity_list[index - 1]['datetime']
            distance = round(geodesic(prev_coords, current_coords).km, 2)
            speed = round(distance / (travel_time.total_seconds() / 3600), 2)
            speed_list.append(speed)
            session_drive += distance
            session_drive = round(session_drive, 2)
            total_drive += session_drive
            energy = round(session_drive * ev_consumption, 2)
            if session_drive > 100.0:
                max_drives.append(activity_list[index])
                max_drive_counter += 1
            print(f'ACTIVITY: Total drive currently: {session_drive} km | Current drive {distance} km | Energy used: {energy} kWh | Travel time: {travel_time} | Speed: {speed} km/h')

        # When drive_session ends (FALSE) reset the session total amount
        if not drive_session:
            session_drive = 0.0

            speed_list = []

    for index, item in enumerate(non_activity_list):
        if index > 0:
            prev_coords = (non_activity_list[index - 1]['lat'], non_activity_list[index - 1]['long'])
            current_coords = (non_activity_list[index]['lat'], non_activity_list[index]['long'])

            # Take dates from current and previous row and calculate the difference
            travel_time = non_activity_list[index]['datetime'] - non_activity_list[index - 1]['datetime']
            distance = round(geodesic(prev_coords, current_coords).km, 2)
            session_drive += distance
            session_drive = round(session_drive, 2)

            print(f'NO ACTIVITY: Total drive currently: {session_drive} km | Current drive {distance} km | Travel time: {travel_time}')

    print(f'Total driven distance with activity: {total_drive} km')
    print(f'Total data points: {data_total}')
    print(f'Data points including activity: {data_activity}')
    print(f'Travel distances driven for over 100 km: {max_drive_counter}')
    print(f'Travel sessions with average speed over 150 km/h: {high_speed_counter}')
    #print(max_drives)

read_points()