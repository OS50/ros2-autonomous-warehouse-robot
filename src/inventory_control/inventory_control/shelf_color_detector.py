import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Int32MultiArray
import cv2
import numpy as np

class ShelfColorDetector(Node):
    def __init__(self):
        super().__init__('shelf_color_detector')

        self.subscription = self.create_subscription(
            CompressedImage, '/camera/image_raw/compressed', self.image_callback, qos_profile_sensor_data
        )
        self.publisher = self.create_publisher(Int32MultiArray, '/shelf_colors', 10)

        # Calibrated Ranges
        self.yellow_range = ((26, 73, 190), (35, 255, 255))
        self.lime_range   = ((43, 79, 0),   (50, 145, 255))
        self.green_range  = ((59, 100, 0),  (75, 204, 255))
        self.purple_range = ((107, 34, 87), (150, 115, 231))
        self.blue_range   = ((92, 73, 0),   (103, 200, 255))

    def image_callback(self, msg):
        np_arr = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None: return

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        counts = [
            self.detect_color(frame, hsv, self.yellow_range, "YEL", (0,255,255)),
            self.detect_color(frame, hsv, self.lime_range,   "LIME", (0,255,0)),
            self.detect_color(frame, hsv, self.green_range,  "GRN", (0,200,0)),
            self.detect_color(frame, hsv, self.purple_range, "PURP", (255,0,255)),
            self.detect_color(frame, hsv, self.blue_range,   "BLUE", (255,0,0))
        ]

        # Publish: [yellow, lime, green, purple, blue]
        msg_out = Int32MultiArray()
        msg_out.data = counts
        self.publisher.publish(msg_out)

        cv2.imshow("Detector", frame)
        cv2.waitKey(1)

    def detect_color(self, frame, hsv, rng, label, color):
        mask = cv2.inRange(hsv, np.array(rng[0]), np.array(rng[1]))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        count = 0
        for c in cnts:
            if cv2.contourArea(c) > 800:
                count += 1
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x,y), (x+w, y+h), color, 2)
                cv2.putText(frame, label, (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return count

def main(args=None):
    rclpy.init(args=args)
    node = ShelfColorDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()