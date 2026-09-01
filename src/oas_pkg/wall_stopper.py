import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class WallStopper(Node):

    def __init__(self):
        super().__init__('wallstopper_node')
        self.publish = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.subscription = self.create_subscription(LaserScan, '/scan', self.wallsub_callback, 10)
        self.subscription  # This line is from the image, though technically not needed

        self.move = Twist()

    def wallsub_callback(self, msg):
        distance = msg.ranges[0]

        if distance > 1:
            self.move.linear.x = 0.5
        else:
            self.move.linear.x = 0.0

        self.publish.publish(self.move)

def main(args=None):
    rclpy.init(args=args)

    wall_stoper = WallStopper()

    rclpy.spin(wall_stoper)

    wall_stoper.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()