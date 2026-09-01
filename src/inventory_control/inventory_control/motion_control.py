import json
import time
import threading
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus
from std_msgs.msg import Int32MultiArray

# Import the GUI
import tkinter as tk
from inventory_control.dashboard import InventoryGUI 

class InventoryMission(Node):
    def __init__(self, gui_app):
        super().__init__('inventory_mission')
        self.gui = gui_app
        
        # === Subscribe to Detector ===
        self.subscription = self.create_subscription(
            Int32MultiArray, '/shelf_colors', self.color_callback, 10
        )
        # Indices: [yellow, lime, green, purple, blue]
        self.latest_colors = [0, 0, 0, 0, 0]
        self.color_names = ["Yellow", "Lime", "Green", "Purple", "Blue"]

        # === Nav2 Client ===
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # === Coordinate Tracking ===
        self.current_pose_str = "0.00, 0.00, 0.00"
        self.current_goal_str = "None"

        # === Shelf Definitions ===
        self.shelves = [
            # Shelf 1 (Green)
            {'pose': self.make_pose(0.52859, -0.0934, 0.6107, 0.65183), 'id': 1, 'correct_idx': 2},
            # Shelf 2 (Purple)
            {'pose': self.make_pose(0.98358, 0.40749, 0.691287, 0.50258), 'id': 2, 'correct_idx': 3},
            # Shelf 3 (Yellow)
            {'pose': self.make_pose(0.32158, 0.43099, 0.69597, 0.708067), 'id': 3, 'correct_idx': 0},
            # Home
            {'pose': self.make_pose(0.0, 0.0, 0.0, 1.0), 'id': 'Home', 'correct_idx': -1}
        ]

        self.results_for_gui = [] 
        self.current_shelf_idx = 0

        # Start Mission Timer
        self.timer = self.create_timer(1.0, self.start_if_ready)
        
        # Placeholder for the scanning timer
        self.scan_timer = None

    def color_callback(self, msg):
        # This keeps updating self.latest_colors constantly
        self.latest_colors = msg.data

    def make_pose(self, x, y, z, w):
        p = PoseStamped()
        p.header.frame_id = 'map'
        p.pose.position.x = float(x)
        p.pose.position.y = float(y)
        p.pose.orientation.z = float(z)
        p.pose.orientation.w = float(w)
        return p

    def start_if_ready(self):
        if not self.client.wait_for_server(timeout_sec=0.0):
            self.get_logger().info("Waiting for Nav2...")
            return
        self.timer.cancel()
        self.go_to_shelf()

    def go_to_shelf(self):
        if self.current_shelf_idx >= len(self.shelves):
            self.finish_mission()
            return

        target = self.shelves[self.current_shelf_idx]
        
        gx = target['pose'].pose.position.x
        gy = target['pose'].pose.position.y
        gw = target['pose'].pose.orientation.w
        self.current_goal_str = f"{gx:.2f}, {gy:.2f}, {gw:.2f}"

        if target['id'] == 'Home':
            msg = "Returning to Start Point..."
        else:
            msg = f"Moving to Shelf {target['id']}..."

        self.update_gui_status(msg)
        self.get_logger().info(msg)

        goal = NavigateToPose.Goal()
        goal.pose = target['pose']
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        future = self.client.send_goal_async(goal, feedback_callback=self.feedback_callback)
        future.add_done_callback(self.nav_response)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        cx = feedback.current_pose.pose.position.x
        cy = feedback.current_pose.pose.position.y
        cw = feedback.current_pose.pose.orientation.w
        self.current_pose_str = f"{cx:.2f}, {cy:.2f}, {cw:.2f}"

    def nav_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected. Skipping.")
            self.current_shelf_idx += 1
            self.go_to_shelf()
            return
        goal_handle.get_result_async().add_done_callback(self.nav_result)

    def nav_result(self, future):
        status = future.result().status
        target = self.shelves[self.current_shelf_idx]
        
        self.update_gui_status(f"Arrived at {target['id']}")

        if status == GoalStatus.STATUS_SUCCEEDED:
            if target['id'] == 'Home':
                self.get_logger().info("Returned to Start Point.")
                self.update_gui_status("Mission Finished at Home.")
                # No next step, we are done or can loop if desired
            else:
                self.update_gui_status(f"Scanning Shelf {target['id']}...")
                self.get_logger().info(f"Arrived at Shelf {target['id']}. Scanning (Waiting 10s)...")
                
                # === THE FIX IS HERE ===
                # Instead of sleeping, we start a timer. 
                # This allows color_callback to keep running in the background.
                self.scan_timer = self.create_timer(10.0, self.finish_scanning_callback)
        else:
            self.get_logger().warn(f"Failed to reach location: {target['id']}")
            self.current_shelf_idx += 1
            self.go_to_shelf()

    def finish_scanning_callback(self):
        # This function runs 10 seconds AFTER arrival
        self.scan_timer.cancel() # Stop the timer
        self.scan_timer = None
        
        target = self.shelves[self.current_shelf_idx]
        
        # Now self.latest_colors contains fresh data!
        self.process_inventory(target)
        
        # Move to next location
        self.current_shelf_idx += 1
        self.go_to_shelf()

    def process_inventory(self, target):
        counts = self.latest_colors
        correct_idx = target['correct_idx']
        
        total_count = sum(counts)
        correct_count = counts[correct_idx]
        misplaced_count = total_count - correct_count
        
        bad_colors = []
        for i, count in enumerate(counts):
            if i != correct_idx and count > 0:
                bad_colors.append(self.color_names[i])
        
        bad_color_str = ", ".join(bad_colors) if bad_colors else "None"

        data = {
            'id': target['id'],
            'total': total_count,
            'misplaced': misplaced_count,
            'bad_colors': bad_color_str
        }
        self.results_for_gui.append(data)
        
        self.update_gui_status(f"Finished Shelf {target['id']}")

    def update_gui_status(self, location_text):
        timestamp = time.strftime("%H:%M:%S")
        self.gui.root.after(0, self.gui.update_dashboard, 
                            location_text, 
                            self.results_for_gui, 
                            timestamp,
                            self.current_pose_str,
                            self.current_goal_str)

    def finish_mission(self):
        self.update_gui_status("Mission Complete")
        self.get_logger().info("Mission Complete. Report Saved.")

def main(args=None):
    rclpy.init(args=args)
    root = tk.Tk()
    app = InventoryGUI(root)
    node = InventoryMission(app)
    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()