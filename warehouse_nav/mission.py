#!/usr/bin/env python3
"""Warehouse delivery mission: Pickup -> Drop-off -> Home using Nav2."""
import math
import time

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration

# Exact Map-frame coordinates matching warehouse.world zones:
# - pickup_zone:  (-4.0,  3.0)
# - dropoff_zone: ( 4.3,  3.0)
# - home_zone:    (-4.0, -4.0)
WAYPOINTS = [
    ('Pickup',   4.3,  3.0, -math.pi / 2.0),
    ('Drop-off', -4.0, -4.0,  0.0),
    ('Home',     -4.0,  3.0,  0.0),
]

MAX_RETRIES = 2
GOAL_TIMEOUT_SEC = 120.0  # Max time allowed per leg before resetting


def make_pose(nav: BasicNavigator, x: float, y: float, yaw: float) -> PoseStamped:
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = 0.0
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def go(nav: BasicNavigator, name: str, x: float, y: float, yaw: float) -> bool:
    for attempt in range(1, MAX_RETRIES + 2):
        if attempt > 1:
            nav.get_logger().warn(
                f'Retry {attempt - 1}/{MAX_RETRIES} for {name}: clearing costmaps first...')
            nav.clearAllCostmaps()
            time.sleep(1.0)

        nav.get_logger().info(
            f'>>> Heading to {name} (x={x:.1f}, y={y:.1f}, yaw={math.degrees(yaw):.0f} deg)')
        nav.goToPose(make_pose(nav, x, y, yaw))

        last_log_time = nav.get_clock().now()

        while not nav.isTaskComplete():
            fb = nav.getFeedback()
            now = nav.get_clock().now()

            if fb:
                # Log progress every 3 seconds of sim time
                if (now - last_log_time) > Duration(seconds=3.0):
                    eta_sec = Duration.from_msg(fb.estimated_time_remaining).nanoseconds * 1e-9
                    nav.get_logger().info(
                        f'    [{name}] {fb.distance_remaining:.2f} m left | '
                        f'ETA: {eta_sec:.1f}s | '
                        f'Recoveries: {fb.number_of_recoveries}')
                    last_log_time = now

                # Cancel and retry if stuck behind dynamic obstacles too long
                if Duration.from_msg(fb.navigation_time) > Duration(seconds=GOAL_TIMEOUT_SEC):
                    nav.get_logger().warn(
                        f'    [{name}] Exceeded {GOAL_TIMEOUT_SEC}s timeout! Canceling task...')
                    nav.cancelTask()
                    break

            time.sleep(0.1)

        result = nav.getResult()
        if result == TaskResult.SUCCEEDED:
            nav.get_logger().info(f'*** Reached {name} successfully!')
            return True

        nav.get_logger().warn(f'{name} failed with status: {result} (attempt {attempt})')

    return False


def main():
    rclpy.init()
    nav = BasicNavigator()

    # Ensure sim time is active on the navigator node
    if not nav.has_parameter('use_sim_time'):
        nav.declare_parameter('use_sim_time', True)
    nav.set_parameters([rclpy.parameter.Parameter(
        'use_sim_time', rclpy.Parameter.Type.BOOL, True)])

    nav.get_logger().info('Waiting for Nav2 to become active...')
    nav.waitUntilNav2Active()
    nav.get_logger().info('Nav2 is active! Starting warehouse delivery mission.')

    start_time = nav.get_clock().now()

    for name, x, y, yaw in WAYPOINTS:
        if not go(nav, name, x, y, yaw):
            nav.get_logger().error(f'Mission aborted at {name} after maximum retries.')
            break
        nav.get_logger().info(f'Simulating load/unload at {name} for 2 seconds...')
        time.sleep(2.0)
    else:
        total_sec = (nav.get_clock().now() - start_time).nanoseconds * 1e-9
        nav.get_logger().info(f'=== Mission complete in {total_sec:.1f}s! ===')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
