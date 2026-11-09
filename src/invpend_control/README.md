# invpend_control

Kontroler PID cascade (Python) untuk inverted pendulum.

```
           x_ref ──►(+)──► PID cart ──► theta_ref ──►(-)──► PID pole ──► F ──► /cart_effort_controller/commands
                     ▲ -x                              ▲ theta
                     └──────────── /joint_states ──────┘
```

- **Outer loop (cart)**: error posisi cart menjadi referensi sudut pole (dibatasi `cart.max_pole_reference`).
  Supaya cart pindah ke +x, pole harus dicondongkan ke +x dulu.
- **Inner loop (pole)**: error sudut pole menjadi gaya ke cart (dibatasi `max_effort`).
- Jika `|theta| > fall_angle`, gaya = 0 sampai pole kembali ke jangkauan.

Konvensi: `theta = 0` tegak, `theta > 0` ujung pole condong ke +x, `F > 0` mendorong cart ke +x.

## Menjalankan

```bash
# simulasi + kontroler
ros2 launch invpend_control control.launch.py
# opsi: push_at_start:=false headless:=true rviz2:=false

# kontroler saja (simulasi sudah jalan di terminal lain)
ros2 launch invpend_control control.launch.py simulation:=false
```

## Memberi gangguan ke pole

Pole adalah joint pasif. Gangguan diberikan sebagai torsi (Nm) lewat topic
`/pole/disturbance` (plugin Gazebo `ApplyJointForce`). Secara default
`control.launch.py` memberi dorongan 2 Nm selama 0.1 s, 2 detik setelah simulasi siap.

```bash
# dorongan singkat (otomatis kembali ke 0)
ros2 run invpend_control push_pole --ros-args -p torque:=-3.0 -p duration:=0.1 -p use_sim_time:=true

# torsi terus-menerus (kirim 0 untuk menghentikan)
ros2 topic pub --once /pole/disturbance std_msgs/msg/Float64 "{data: 1.0}"
```

## Tuning saat runtime

```bash
ros2 param set /pid_controller pole.kp 400.0
ros2 param set /pid_controller cart.kd 0.3
ros2 topic pub --once /pid_controller/cart_setpoint std_msgs/msg/Float64 "{data: 1.0}"
```

Atau gunakan `rqt` → Plugins → Configuration → Parameter Reconfigure.
Nilai default ada di `config/pid_config.yaml`.
