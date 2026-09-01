import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MoveTurtlebot(Node):

    def __init__(self):
        super().__init__('move_turtlebot3_node')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 1)
        self.time_passed = 0
        timer_period = 0.5
        self.move = Twist()
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        if self.time_passed < 20:
            self.move.linear.x = 0.5
            self.move.angular.z = 0.5
        else:
            self.move.linear.x = 0.0
            self.move.angular.z = 0.0
        self.pub.publish(self.move)
        self.time_passed += 0.5

def main(args=None):
    rclpy.init(args=args)
    
    move_turtlebot = MoveTurtlebot()
    
    rclpy.spin(move_turtlebot)

if __name__ == '__main__':
    main()