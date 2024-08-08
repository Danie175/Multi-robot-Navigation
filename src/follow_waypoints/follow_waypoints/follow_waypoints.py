#! /usr/bin/env python3
# Copyright 2021 Samsung Research America
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from copy import deepcopy

from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
import rclpy
#
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
#
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult



#
def parse_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        
    machine_sequences = []
    
    for amr in data['amr_list']:
        machine_sequences.append(amr['machine_sequence'])
        
    amr1_sequence = machine_sequences[0]
    return amr1_sequence

class JSONFileHandler(FileSystemEventHandler):
    def __init__(self, file_path, callback):
        self.file_path = file_path
        self.callback = callback
        self.callback_called = False

    def on_modified(self, event):
        if event.src_path == self.file_path and not self.callback_called:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            self.callback(data)
            self.callback_called = True

def wait_for_json_update(file_path, callback):
    event_handler = JSONFileHandler(file_path, callback)
    observer = Observer()
    observer.schedule(event_handler, path=file_path, recursive=False)
    observer.start()

    try:
        while not event_handler.callback_called:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.stop()
    observer.join()

def on_json_update(data):
    print("JSON file updated with new values:")
    print(data)
    # You can put the main execution code here or continue in another function

    start_execution(data)  # Call the main execution function
#
def start_execution(data):
    rclpy.init()

    navigator = BasicNavigator()

    m1 = [-1.59, 4.42]
    m2 = [-1.709, -3.71]
    m3 = [4.23, 4.37]
    m4 = [4.1, -3.67]
    loading_dock = [-7.33, 0.480]
    unloading_dock = [6.32, 0.42]

    poses = {
        '0': m1,
        '1': m2,
        '2': m3,
        '3': m4,
        '-1': loading_dock,
        '-2': unloading_dock
    }

    inspection_route = []
    json_file_path = '/home/daniel/CustomMultibot/src/JobShopGA/amr_data.json'
    sequence = parse_json(json_file_path)

    for m in sequence:
        inspection_route.append(poses[str(m)])

    # Set our demo's initial pose
    # initial_pose = PoseStamped()
    # initial_pose.header.frame_id = 'map'
    # initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    # initial_pose.pose.position.x = -0.004
    # initial_pose.pose.position.y = -0.041
    # initial_pose.pose.orientation.z = 1.0
    # initial_pose.pose.orientation.w = 0.0
    # navigator.setInitialPose(initial_pose)

    # Wait for navigation to fully activate
    # navigator.waitUntilNav2Active()

    while rclpy.ok():

        # Send our route
        inspection_points = []
        inspection_pose = PoseStamped()
        inspection_pose.header.frame_id = 'map'
        inspection_pose.header.stamp = navigator.get_clock().now().to_msg()
        inspection_pose.pose.orientation.z = 1.0
        inspection_pose.pose.orientation.w = 0.0
        for pt in inspection_route:
            inspection_pose.pose.position.x = pt[0]
            inspection_pose.pose.position.y = pt[1]
            inspection_points.append(deepcopy(inspection_pose))
        nav_start = navigator.get_clock().now()
        navigator.followWaypoints(inspection_points)

        # Do something during our route (e.x. AI to analyze stock information or upload to the cloud)
        # Simply print the current waypoint ID for the demonstration
        i = 0
        while not navigator.isTaskComplete():
            i += 1
            feedback = navigator.getFeedback()
            if feedback and i % 5 == 0:
                print('Executing current waypoint: ' +
                      str(feedback.current_waypoint + 1) + '/' + str(len(inspection_points)))

        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print('Inspection of shelves complete! Returning to start...')
        elif result == TaskResult.CANCELED:
            print('Inspection of shelving was canceled. Returning to start...')
            exit(1)
        elif result == TaskResult.FAILED:
            print('Inspection of shelving failed! Returning to start...')

        # Uncomment to go back to start
        # initial_pose.header.stamp = navigator.get_clock().now().to_msg()
        # navigator.goToPose(initial_pose)
        # while not navigator.isTaskComplete():
        #     pass

#
def main():
    json_file_path = '/home/daniel/CustomMultibot/src/JobShopGA/amr_data.json'
    wait_for_json_update(json_file_path, on_json_update)
#
if __name__ == '__main__':
    main()
