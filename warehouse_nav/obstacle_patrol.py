#!/usr/bin/env python3
"""Drives multiple moving obstacles at independent speeds and axes."""
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MultiObstaclePatrol(Node):
    def __init__(self):
        super().__init__('obstacle_patrol')

        # Define each obstacle's patrol configuration:
        # - name: matches the namespace in gen_world.py (/obstacle_1, etc.)
        # - axis: 'x' (East-West) or 'y' (North-South)
        # - span: one-way travel distance in meters from spawn point
        # - speed: base speed in m/s (vary these per obstacle!)
        # - start_dir: 1.0 (positive axis) or -1.0 (negative axis)
        # - vary_speed: True to modulate speed smoothly between 50% and 150%
        self.obstacles = [
            {
                'name': 'obstacle_1',
                'axis': 'x',
                'span': 5.5,          # moves from x = -2.5 to x = +4.0
                'speed': 0.12,        # medium speed (0.18 m/s)
                'start_dir': 1.0,
                'vary_speed': True,
            },
            {
                'name': 'obstacle_2',
                'axis': 'y',
                'span': 5.5,          # moves from y = -1.0 to y = +3.5 in Aisle 1
                'speed': 0.13,        # slow speed (0.18 m/s)
                'start_dir': 1.0,
                'vary_speed': False,
            },
            {
                'name': 'obstacle_3',
                'axis': 'y',
                'span': 5.0,          # moves from y = +3.5 to y = -1.0 in Aisle 2
                'speed': 0.13,        # fast speed (0.20 m/s)
                'start_dir': -1.0,
                'vary_speed': True,
            },
        ]

        # Initialize state and publisher for each obstacle
        for obs in self.obstacles:
            obs['pub'] = self.create_publisher(
                Twist, f"/{obs['name']}/cmd_vel", 10)
            obs['dir'] = obs['start_dir']
            obs['half_period'] = obs['span'] / obs['speed']
            obs['leg_start'] = None

        self.create_timer(0.05, self.tick)  # 20 Hz control loop

    def tick(self):
        now = self.get_clock().now()
        if now.nanoseconds == 0:
            return

        for obs in self.obstacles:
            if obs['leg_start'] is None:
                obs['leg_start'] = now

            elapsed = (now - obs['leg_start']).nanoseconds * 1e-9
            if elapsed >= obs['half_period']:
                obs['dir'] *= -1.0
                obs['leg_start'] = now
                elapsed = 0.0

            # Optional smooth speed variation within each leg (averages to obs['speed'])
            current_speed = obs['speed']
            if obs['vary_speed']:
                phase = (elapsed / obs['half_period']) * 2.0 * math.pi
                current_speed = obs['speed'] * (1.0 + 0.4 * math.cos(phase))

            vel = obs['dir'] * current_speed
            msg = Twist()
            if obs['axis'] == 'x':
                msg.linear.x = vel
            else:
                msg.linear.y = vel

            obs['pub'].publish(msg)


def main():
    rclpy.init()
    rclpy.spin(MultiObstaclePatrol())


if __name__ == '__main__':
    main()
