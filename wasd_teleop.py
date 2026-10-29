
#!/usr/bin/env python3

import sys
import select
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class WASDTeleop(Node):
    def __init__(self):
        super().__init__('wasd_teleop')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.linear_speed = 0.3
        self.angular_speed = 0.8
        self.speed_step = 0.1
        self.min_speed = 0.1
        self.max_speed = 1.0

    def move(self, key):
        msg = Twist()

        if key == 'i':
            self.linear_speed = min(
                self.linear_speed + self.speed_step, self.max_speed
            )
            self.angular_speed = min(
                self.angular_speed + self.speed_step, 2.0
            )
            print(f"Linear: {self.linear_speed:.1f} m/s | "
                  f"Angular: {self.angular_speed:.1f} rad/s")

        elif key == 'k':
            self.linear_speed = max(
                self.linear_speed - self.speed_step, self.min_speed
            )
            self.angular_speed = max(
                self.angular_speed - self.speed_step, 0.1
            )
            print(f"Linear: {self.linear_speed:.1f} m/s | "
                  f"Angular: {self.angular_speed:.1f} rad/s")

        elif key == 'w':
            msg.linear.x = self.linear_speed
        elif key == 's':
            msg.linear.x = -self.linear_speed
        elif key == 'a':
            msg.angular.z = self.angular_speed
        elif key == 'd':
            msg.angular.z = -self.angular_speed

        self.pub.publish(msg)


def main():
    rclpy.init()
    node = WASDTeleop()
    settings = termios.tcgetattr(sys.stdin)

    print("""
===== ROS 2 WASD TELEOP =====
W : Forward
S : Backward
A : Turn left
D : Turn right
I : Increase speed
K : Decrease speed
SPACE : Stop
CTRL+C : Exit
=============================
""")

    try:
        tty.setcbreak(sys.stdin.fileno())

        while True:
            ready, _, _ = select.select([sys.stdin], [], [], 0.05)

            if ready:
                key = sys.stdin.read(1)

                if key == '\x03':
                    break

                node.move(key.lower())

    finally:
        node.pub.publish(Twist())
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

