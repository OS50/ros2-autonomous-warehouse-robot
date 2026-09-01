import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

class MyPublisher(Node):

    def __init__(self):
        super().__init__('robot_location_publisher')
        # Setup publisher: Topic 'robot_location', Queue size 10
        self.pub = self.create_publisher(Point, 'robot_location', 10)
        
        # Initialise the location of the robot
        self.location = Point()
        self.location.x = 10.0
        self.location.y = 10.0
        self.location.z = 10.0
        
        # Setup a timer to update the position at a rate of 10 Hz (0.1s)
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        # Publish location
        self.pub.publish(self.location)
        self.get_logger().info('Publishing location: %f, %f' % (self.location.x, self.location.y))
        
        # Simulate a move
        self.location.x += 1.0
        self.location.y += 2.0

def main(args=None):
    rclpy.init(args=args)
    robot_publisher = MyPublisher()
    rclpy.spin(robot_publisher)
    
    # Clean up
    robot_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()