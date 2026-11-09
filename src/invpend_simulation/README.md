# invpend_simulation

Simulasi inverted pendulum di Gazebo Harmonic menggunakan `gz_ros2_control`.

## Struktur

```
config/
  invpend.gazebo.controllers.yaml   # controller_manager + controller
  invpend.bridge.yaml               # ros_gz_bridge (/clock)
urdf/
  invpend.gazebo.urdf.xacro         # description + ros2_control
  invpend.gazebo.ros2_control.xacro # hardware gz_ros2_control/GazeboSimSystem
worlds/invpend.sdf
launch/simulation.launch.py
```

## Controller

| Controller               | Tipe                                           | Joint            |
|--------------------------|------------------------------------------------|------------------|
| `cart_effort_controller` | `effort_controllers/JointGroupEffortController` | `slider_to_cart` |
| `joint_state_broadcaster`| `joint_state_broadcaster/JointStateBroadcaster` | semua joint      |

- Perintah gaya cart: `/cart_effort_controller/commands` (`std_msgs/msg/Float64MultiArray`, satuan N)
- State joint: `/joint_states`

`cart_to_pole` hanya punya state interface (pasif). Gangguan ke pole diberikan di luar
ros2_control lewat plugin `gz::sim::systems::ApplyJointForce`:

- `/pole/disturbance` (`std_msgs/msg/Float64`, satuan Nm), di-bridge ke
  `/model/invpend/joint/cart_to_pole/cmd_force`. Nilai terakhir terus diterapkan sampai dikirim 0.

> `initial_value` pada state interface pole sengaja tidak dipakai: `gz_ros2_control`
> hanya mereset posisi joint yang punya command interface `position`, dan menambahkan
> interface itu membuat pole tertahan (tidak pasif lagi).

## Menjalankan

```bash
ros2 launch invpend_simulation simulation.launch.py
# opsi: headless:=true rviz2:=false
```

Uji manual tanpa controller (dorong cart dengan gaya 20 N):

```bash
ros2 topic pub --once /cart_effort_controller/commands std_msgs/msg/Float64MultiArray "{data: [20.0]}"
```
