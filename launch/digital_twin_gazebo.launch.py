import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, SetParameter

def generate_launch_description():
    # パッケージパスの取得
    pkg_vla_sim = get_package_share_directory('vla_manipulator_sim')
    pkg_real_driver = get_package_share_directory('feetech_ros2_driver') # 🌟実機ドライバ
    pkg_moveit_config = get_package_share_directory('vla_manipulator_moveit_config')

    # 1. シミュレーション（Gazebo）側の起動
    # さきほどリネームしたGazebo起動ファイルを呼び出します
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_vla_sim, 'launch', 'spawn_robot_gazebo.launch.py')
        )
    )

    # 2. 実機（feetech_ros2_driver）側の起動
    # 実機を動かす時に使っているドライバのLaunchを指定してください
    # (ファイル名が異なる場合は、実際の .launch.py 名に合わせてください)
    real_robot_driver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_real_driver, 'launch', 'feetech_drive.launch.py')
        )
    )

    return LaunchDescription([
        gazebo_sim,
        real_robot_driver
    ])