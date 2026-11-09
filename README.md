# PKC

ros2 launch invpend_description display.launch.py     # cek model di RViz
ros2 launch invpend_simulation simulation.launch.py   # simulasi saja
ros2 launch invpend_control control.launch.py         # simulasi + PID
ros2 topic pub --once /pid_controller/cart_setpoint std_msgs/msg/Float64 "{data: 1.0}"