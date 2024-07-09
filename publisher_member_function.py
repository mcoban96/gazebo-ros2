from PyQt5.QtWidgets import *
import sys
import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MinimalPublisher(Node):
    def __init__(self, topic_name):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(Twist, topic_name, 10)

    def publish_once(self):
        msg = Twist()
        msg.linear.x = 2.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 1.8

        self.publisher_.publish(msg)

class ROS2Thread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.node = None
        self._stop_event = threading.Event()

    def run(self):
        rclpy.init(args=None)
        while not self._stop_event.is_set():
            if self.node:
                rclpy.spin_once(self.node, timeout_sec=0.1)

    def stop(self):
        self._stop_event.set()
        if self.node:
            self.node.destroy_node()
        rclpy.shutdown()

    def set_publisher_topic(self, topic_name):
        if self.node:
            self.node.destroy_node()
        self.node = MinimalPublisher(topic_name)

    def publish_once(self):
        if self.node:
            self.node.publish_once()

class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle("Gazebo+ROS2")
        self.setGeometry(100, 100, 300, 400)
        self.formGroupBox = QGroupBox()

        self.VehicleBox = QComboBox()
        self.VehicleBox.addItems([ "Blue Vehicle","Red Vehicle"])


        self.createForm()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.getInfo)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

        self.ros2_thread = ROS2Thread()
        self.ros2_thread.start()

    def getInfo(self):
        vehicle = self.VehicleBox.currentText()
        if vehicle == "Blue Vehicle":
            self.ros2_thread.set_publisher_topic('/cmd_vel')
        elif vehicle == "Red Vehicle":
            self.ros2_thread.set_publisher_topic('/cmd_vel2')
        
        self.ros2_thread.publish_once()

    def createForm(self):
        layout = QFormLayout()
        layout.addRow(QLabel("Vehicle"), self.VehicleBox)
        self.formGroupBox.setLayout(layout)

    def closeEvent(self, event):
        self.ros2_thread.stop()
        self.ros2_thread.join()
        event.accept()

def main(args=None):
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
