import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

class MySubscriber(Node):

    def __init__(self):
        super().__init__('robot_location_subscriber')
        # Setup subscription to 'robot_location'
        self.subscription = self.create_subscription(Point, 'robot_location', self.location_callback, 10)
        self.subscription  # Prevent unused variable warning

    def location_callback(self, location):
        self.get_logger().info('Received robot location: %f, %f' % (location.x, location.y))

def main(args=None):
    rclpy.init(args=args)
    robot_location_subscriber = MySubscriber()
    rclpy.spin(robot_location_subscriber)
    
    # Clean up
    robot_location_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()