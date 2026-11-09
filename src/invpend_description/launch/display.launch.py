from launch import LaunchDescription
from launch.substitutions import Command, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package = FindPackageShare('invpend_description')
    urdf = PathJoinSubstitution([package, 'urdf', 'invpend.urdf.xacro'])
    rviz_config = PathJoinSubstitution([package, 'config', 'urdf.rviz'])

    # robot state publisher node
    robot_description = ParameterValue(Command(['xacro ', urdf]), value_type=str)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description}
        ]
    )

    # joint state publisher node
    jsp_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
    )

    # RViz2 node
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config]
    )

    # add nodes
    node_list = [
        jsp_gui_node,
        robot_state_publisher_node,
        rviz2_node,
    ]

    return LaunchDescription(node_list)
