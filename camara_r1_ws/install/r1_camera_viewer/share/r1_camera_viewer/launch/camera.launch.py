from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'resolution',
            default_value='360p',
            description='Resolución del stream: 180p, 360p, 720p'
        ),
        Node(
            package='r1_camera_viewer',
            executable='camera_viewer',
            name='r1_camera_viewer',
            parameters=[{'resolution': LaunchConfiguration('resolution')}],
            output='screen',
        ),
    ])
