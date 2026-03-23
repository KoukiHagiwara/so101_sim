## 実行方法
1. GazeboとMoveIt(vla_manipulator_moveit_configパッケージ)の起動
```
$  ros2 launch so101_sim spawn_robot_gazebo.launch.py
```

- Gazeboで学習がうまくいっているか試すコマンド
- それぞれ数字ごとに別のターミナルを開いて実行
1. Gazeboの起動
```
$  ros2 launch so101_sim spawn_robot_gazebo.launch.py
```
2. MoveItの起動
```
$  ros2 launch vla_manipulator_moveit_config demo.launch.py use_sim_time:=true
```
3. コントローラーの切り替え
```
$  ros2 control switch_controllers \
  --deactivate arm_controller gripper_controller \
  --activate ai_position_controller ai
```
4. AIノードの起動
```
$  cd lerobot
```
```
$  pixi run python act_inference_node.py
```

## 補足
- plan&executeを廃止し、AIから直接モータの値を読み込むコマンド
- これを実行することでJointTrajectoryControllerからJointGroupPositionControllerに切り替わる
- 元に戻したい時は、--deactivate と --activate の名前を逆にすればOK
```
$  ros2 control switch_controllers \
  --deactivate arm_controller gripper_controller \
  --activate ai_position_controller ai_gripper_controller
```