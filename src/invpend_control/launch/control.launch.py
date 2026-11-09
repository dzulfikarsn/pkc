from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Arguments
    simulation = LaunchConfiguration('simulation')
    headless = LaunchConfiguration('headless')
    rviz2 = LaunchConfiguration('rviz2')
    use_sim_time = LaunchConfiguration('use_sim_time')
    push_at_start = LaunchConfiguration('push_at_start')
    argument_list = [
        DeclareLaunchArgument(
            'simulation',
            default_value='true',
            choices=['true', 'false'],
            description='Jika diatur true, simulasi Gazebo (invpend_simulation) ikut dijalankan.'
        ),
        DeclareLaunchArgument(
            'headless',
            default_value='false',
            choices=['true', 'false'],
            description='Jika diatur true, Window simulasi akan tidak ditampilkan dan simulasi tetap berjalan di latar belakang.'
        ),
        DeclareLaunchArgument(
            'rviz2',
            default_value='true',
            choices=['true', 'false'],
            description='Jika diatur true, node RViz2 akan dijalankan.'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            choices=['true', 'false'],
            description='Jika diatur true, seluruh node yang diatur parameter use_sim_time: true akan menggunakan clock dari simulasi (/clock).'
        ),
        DeclareLaunchArgument(
            'push_at_start',
            default_value='true',
            choices=['true', 'false'],
            description='Jika diatur true, pole diberi dorongan torsi singkat (push_pole) setelah simulasi siap.'
        )
    ]

    # Inverted Pendulum Simulation
    simulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('invpend_simulation'), 'launch', 'simulation.launch.py'
            ])
        ]),
        launch_arguments={
            'headless': headless,
            'rviz2': rviz2,
            'use_sim_time': use_sim_time
        }.items(),
        condition=IfCondition(simulation)
    )

    pid_config = PathJoinSubstitution([
        FindPackageShare('invpend_control'), 'config', 'pid_config.yaml'
    ])

    pid_controller_node = Node(
        package='invpend_control',
        executable='pid_controller',
        name='pid_controller',
        output='screen',
        parameters=[pid_config, {'use_sim_time': use_sim_time}]
    )

    # Dorongan awal ke pole supaya kerja kontroler terlihat
    push_pole_node = Node(
        package='invpend_control',
        executable='push_pole',
        name='push_pole',
        output='screen',
        parameters=[{'torque': 2.0, 'duration': 0.1, 'delay': 2.0, 'use_sim_time': use_sim_time}],
        condition=IfCondition(push_at_start)
    )

    # Process List
    process_list = [
        simulation_launch,
        pid_controller_node,
        push_pole_node
    ]

    return LaunchDescription(argument_list + process_list)
