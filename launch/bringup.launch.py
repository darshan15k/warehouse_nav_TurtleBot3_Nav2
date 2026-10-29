import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('warehouse_nav')
    nav2 = get_package_share_directory('nav2_bringup')

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'sim.launch.py')))

    nav = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('params_file'),
            'use_sim_time': 'true',
            'autostart': 'true',
        }.items())

    rviz = Node(
        package='rviz2', executable='rviz2', output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': True}])

    patrol = Node(
        package='warehouse_nav', executable='obstacle_patrol', output='screen',
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('obstacle')))

    return LaunchDescription([
        DeclareLaunchArgument(
            'map', default_value=os.path.join(pkg, 'maps', 'warehouse.yaml')),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg, 'config', 'nav2_params.yaml')),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(nav2, 'rviz', 'nav2_default_view.rviz')),
        DeclareLaunchArgument('obstacle', default_value='true'),
        sim,
        nav,
        rviz,
        patrol,
    ])
