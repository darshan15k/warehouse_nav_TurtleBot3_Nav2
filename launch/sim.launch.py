import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    pkg = get_package_share_directory('warehouse_nav')
    tb3 = get_package_share_directory('turtlebot3_gazebo')
    gz = get_package_share_directory('gazebo_ros')
    world = os.path.join(pkg, 'worlds', 'warehouse.world')

    def inc(path, args=None):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(path),
            launch_arguments=(args or {}).items())

    return LaunchDescription([
        inc(os.path.join(gz, 'launch', 'gzserver.launch.py'), {'world': world}),
        inc(os.path.join(gz, 'launch', 'gzclient.launch.py')),
        inc(os.path.join(tb3, 'launch', 'robot_state_publisher.launch.py'),
            {'use_sim_time': 'true'}),
        inc(os.path.join(tb3, 'launch', 'spawn_turtlebot3.launch.py'),
            {'x_pose': '-4.0', 'y_pose': '-4.0'}),
    ])
