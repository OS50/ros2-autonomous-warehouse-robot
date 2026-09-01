import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan

class LidarSubscriber(Node):

    def __init__(self):
        super().__init__('lidar_subscriber')
        self.subscription = self.create_subscription(LaserScan, '/scan', self.lidar_callback, 5)
        self.subscription  # This line is from the image, though technically not needed

    def lidar_callback(self, msg):
        print(msg.ranges[0])

def main(args=None):
    rclpy.init(args=args)

    lidar_subscriber = LidarSubscriber()

    rclpy.spin(lidar_subscriber)

    lidar_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()