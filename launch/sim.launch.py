import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    tb3_model = os.environ.get('TURTLEBOT3_MODEL', 'waffle')
    pkg = get_package_share_directory('warehouse_nav')
    tb3 = get_package_share_directory('turtlebot3_gazebo')
    gz = get_package_share_directory('gazebo_ros')
    world = os.path.join(pkg, 'worlds', 'warehouse.world')
    sdf_path = os.path.join(tb3, 'models', f'turtlebot3_{tb3_model}', 'model.sdf')
    
    def inc(path, args=None):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(path),
            launch_arguments=(args or {}).items())
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', tb3_model,
            '-file', sdf_path,
            '-x', '-4.0',
            '-y', '-4.0',
            '-z', '0.05',
            '-Y', '0.0',
        ],
        output='screen',
    )
    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', tb3_model),
        inc(os.path.join(gz, 'launch', 'gzserver.launch.py'), {'world': world}),
        inc(os.path.join(gz, 'launch', 'gzclient.launch.py')),
        inc(os.path.join(tb3, 'launch', 'robot_state_publisher.launch.py'),
            {'use_sim_time': 'true'}),
            
        # Delay spawning 2 seconds, gzserver physics initialized
        TimerAction(period=2.0, actions=[spawn_robot]),
    ])
