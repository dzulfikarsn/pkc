"""
Memberi dorongan (torsi) singkat ke pole untuk menguji kontroler.

Publish torsi ke /pole/disturbance selama `duration` detik (waktu simulasi)
setelah menunggu `delay` detik, lalu kirim 0 dan keluar.

Contoh:
    ros2 run invpend_control push_pole --ros-args -p torque:=-3.0 -p use_sim_time:=true
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class PushPole(Node):

    def __init__(self):
        super().__init__('push_pole')
        # torsi (Nm), positif = pole condong ke +x
        self.torque = self.declare_parameter('torque', 2.0).value
        self.duration = self.declare_parameter('duration', 0.1).value  # s
        self.delay = self.declare_parameter('delay', 0.0).value        # s
        topic = self.declare_parameter('topic', '/pole/disturbance').value

        self.pub = self.create_publisher(Float64, topic, 10)
        self.start_time = None
        self.done = False
        self.create_timer(0.005, self.update)

    def update(self):
        now = self.get_clock().now().nanoseconds * 1e-9
        if now == 0.0:
            return  # /clock belum diterima
        # tunggu sampai bridge Gazebo terhubung
        if self.pub.get_subscription_count() == 0:
            return
        if self.start_time is None:
            self.start_time = now + self.delay
            return

        elapsed = now - self.start_time
        if elapsed < 0.0:
            return
        if elapsed < self.duration:
            self.pub.publish(Float64(data=float(self.torque)))
            return

        self.pub.publish(Float64(data=0.0))
        self.get_logger().info(
            f'dorongan {self.torque:+.2f} Nm selama {self.duration:.2f} s selesai')
        self.done = True


def main(args=None):
    rclpy.init(args=args)
    node = PushPole()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
