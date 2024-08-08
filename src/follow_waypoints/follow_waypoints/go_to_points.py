import time
import json
import threading
from geometry_msgs.msg import PoseStamped
import rclpy
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.executors import MultiThreadedExecutor

def parse_json(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
        
        machine_sequences = []
        ptime_sequences = []
        
        for amr in data.get('amr_list', []):
            machine_sequences.append(amr.get('machine_sequence', []))
            ptime_sequences.append(amr.get('ptime_sequence', []))
        
        new_machine_sequences = [
            [machine for machine, ptime in zip(machines, ptimes) if ptime != 0]
            for machines, ptimes in zip(machine_sequences, ptime_sequences)
        ]
        new_ptime_sequences = [
            [ptime for ptime in ptimes if ptime != 0]
            for ptimes in ptime_sequences
        ]

        return new_machine_sequences, new_ptime_sequences
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

class JSONFileHandler(FileSystemEventHandler):
    def __init__(self, file_path, callback):
        self.file_path = file_path
        self.callback = callback

    def on_modified(self, event):
        if event.src_path == self.file_path:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            self.callback(data)

def wait_for_json_update(file_path, callback):
    event_handler = JSONFileHandler(file_path, callback)
    observer = Observer()
    observer.schedule(event_handler, path=file_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.stop()
    observer.join()

def robot_process(navigator, sequence, ptimes, robot_namespace):
    poses = {
        '0': [-3.32, 6.65],
        '1': [-3.38, 1.46],
        '2': [1.627, 6.459],
        '3': [1.681, 1.407],
        '-1': [-6.69, 4.028],
        '-2': [3.52, 3.96]
    }

    for i, m in enumerate(sequence):
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = poses[str(m)][0]
        goal_pose.pose.position.y = poses[str(m)][1]
        goal_pose.pose.orientation.w = 1.0

        print(f'{robot_namespace} Going to {m}')
        navigator.goToPose(goal_pose)

        while not navigator.isTaskComplete():
            time.sleep(1)

        if i < len(ptimes):
            print(f'{robot_namespace} Job being processed for {ptimes[i]} seconds')
            time.sleep(ptimes[i])

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print(f'{robot_namespace} Task completed successfully.')
    elif result == TaskResult.CANCELED:
        print(f'{robot_namespace} Task was canceled.')
    elif result == TaskResult.FAILED:
        print(f'{robot_namespace} Task failed.')

def manage_threads(robot_namespaces, sequences, ptimes, executor):
    navigators = []
    threads = []

    for i, namespace in enumerate(robot_namespaces):
        if i >= len(sequences):
            break
        
        print(f"Initializing {namespace}")
        navigator = BasicNavigator(namespace=namespace)
        navigators.append(navigator)

        sequence = sequences[i]
        ptime = ptimes[i]

        thread = threading.Thread(target=robot_process, args=(navigator, sequence, ptime, namespace))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # for navigator in navigators:
        # navigator.shutdown()

def start_execution(sequences, ptimes):
    rclpy.init()

    robot_namespaces = ['robot1', 'robot2']  # Example namespaces

    # Use a single MultiThreadedExecutor
    executor = MultiThreadedExecutor()

    # Manage threads based on the namespaces
    manage_threads(robot_namespaces, sequences, ptimes, executor)

    # rclpy.shutdown()

def on_json_update(data):
    print("JSON file updated with new values:")
    print(data)
    
    sequences, ptimes = parse_json('/home/daniel/Multi-robot-Navigation/src/JobShopGA/amr_data.json')
    
    if sequences is None:
        print("Failed to parse JSON file, exiting.")
        return

    start_execution(sequences, ptimes)

def main():
    print('Waiting for JSON file update...')
    json_file_path = '/home/daniel/Multi-robot-Navigation/src/JobShopGA/amr_data.json'
    wait_for_json_update(json_file_path, on_json_update)

if __name__ == '__main__':
    main()
