import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from geometry_msgs.msg import PointStamped

class Publisher(Node):
    def __init__(self, namespace):
        super().__init__('initial_pose_pub_node')
        self.namespace = namespace

        # Create publisher and subscriber with the namespace
        self.publisher_ = self.create_publisher(PoseWithCovarianceStamped, f'{self.namespace}/initialpose', 1)
        self.subscriber_ = self.create_subscription(PointStamped, f'{self.namespace}/clicked_point', self.callback, 1)
        self.subscriber_  # prevent unused variable warning

    def callback(self, msg):
        self.get_logger().info('Received Data:\n X : %f \n Y : %f \n Z : %f' % (msg.point.x, msg.point.y, msg.point.z))
        self.publish(msg.point.x, msg.point.y, msg.point.z)

    def publish(self, x, y, theta):
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        msg.pose.pose.orientation.w = theta
        self.get_logger().info(f'Publishing Initial Position to {self.namespace} \n X= {x} \n Y= {y} \n W = {theta} ')
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    if len(sys.argv) < 2:
        print("Usage: ros2 run <package_name> set_initial_pose.py <namespace>")
        return

    namespace = sys.argv[1]

    publisher = Publisher(namespace)
    rclpy.spin(publisher)
    publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
