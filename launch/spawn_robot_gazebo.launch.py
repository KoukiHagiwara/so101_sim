import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution, Command
from launch_ros.actions import Node, SetParameter
from launch.actions import TimerAction

def generate_launch_description():
    pkg_vla_manipulator = get_package_share_directory('vla_manipulator')
    pkg_so101_sim = get_package_share_directory('so101_sim')
    moveit_config_dir = get_package_share_directory('so101_moveit_jazzy')
    
    # 1. XACRO で URDF を生成
    xacro_file = os.path.join(moveit_config_dir, 'config', 'so101_new_calib.urdf.xacro')
    # 🌟 hardware_type を引数で渡し、URDF内で gz_ros2_control を読み込むようにします
    robot_desc_cmd = Command(['xacro ', xacro_file, ' hardware_type:=gazebo'])

    workspace_share_dir = os.path.abspath(os.path.join(pkg_vla_manipulator, '..'))
    
    # 🌟 環境変数を Gazebo Harmonic 用 (GZ_SIM) に統一
    resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    set_gz_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH', 
        value=f'{workspace_share_dir}:{resource_path}'
    )
    
    # シミュレーション時間を使用
    set_sim_time = SetParameter(name='use_sim_time', value=True)
    
    # ワールドファイルのパス
    world_file = os.path.join(pkg_so101_sim, 'worlds', 'so101_env.sdf')
    
    # 🌟 Gazebo Sim (Harmonic) の起動
    # ros_ign_sim -> ros_gz_sim に変更
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
        ]),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[{'robot_description': robot_desc_cmd, 'use_sim_time': True}]
    )

    # 🌟 Gazeboにロボットをスポーンさせる (ros_gz_sim)
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'so101',
            '-topic', 'robot_description',
        ],
        output='screen',
    )
    
    # 🌟 Clock ブリッジのメッセージタイプを Harmonic 用に変更
    # [ignition.msgs.Clock -> [gz.msgs.Clock
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    # カメラ映像等のブリッジ設定
    bridge_params = os.path.join(pkg_so101_sim, 'config', 'bridge.yaml')
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '-p', f'config_file:={bridge_params}',
        ],
        output='screen'
    )

    # 🌟 コントローラの Spawner
    jsb_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )
    arm_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
    )
    gripper_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller"],
    )

    # 🌟 追記：AI用コントローラー（最初は待機状態 --inactive）
    ai_arm_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ai_position_controller", "--inactive"],
    )
    ai_gripper_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ai_gripper_controller", "--inactive"],
    )

    # MoveIt 2 本体と RViz
    move_group = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moveit_config_dir, 'launch', 'move_group.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moveit_config_dir, 'launch', 'moveit_rviz.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # ==========================================
    # 🌟 Gazeboの準備を「3秒待ってから」Spawnerを起動
    # ==========================================
    delayed_spawners = TimerAction(
        period=3.0,
        actions=[
            jsb_spawner,
            arm_spawner,
            gripper_spawner,
            ai_arm_spawner,
            ai_gripper_spawner
        ]
    )

    return LaunchDescription([
        set_sim_time,
        set_gz_model_path,
        gz_sim,
        robot_state_publisher,
        spawn,
        clock_bridge,
        ros_gz_bridge,
        move_group,  
        rviz,
        delayed_spawners
    ])