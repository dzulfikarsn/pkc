"""
Kontroler PID cascade untuk inverted pendulum (cart-pole).

Konvensi (lihat invpend_description):
    x      : posisi cart (m), joint slider_to_cart
    theta  : sudut pole (rad), joint cart_to_pole, 0 = tegak,
             positif = ujung pole condong ke +x
    F      : gaya ke cart (N), positif = dorong ke +x

Struktur kontrol:
    outer loop (cart)  : theta_ref = PID_cart(x_ref - x, -x_dot)
                         -> supaya cart bergerak ke +x, pole harus dicondongkan ke +x dulu
    inner loop (pole)  : F = PID_pole(theta - theta_ref, theta_dot)
                         -> pole condong ke +x, cart didorong ke +x untuk "menangkap" pole
"""

import math

from invpend_control.pid import PID
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64, Float64MultiArray


def wrap_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class PIDController(Node):

    def __init__(self):
        super().__init__('pid_controller')

        self.declare_parameters('', [
            ('rate', 100.0),
            ('cart_joint', 'slider_to_cart'),
            ('pole_joint', 'cart_to_pole'),
            ('command_topic', '/cart_effort_controller/commands'),
            ('max_effort', 100.0),
            ('fall_angle', 0.6),
            ('cart_setpoint', 0.0),
            ('pole.kp', 600.0),
            ('pole.ki', 0.0),
            ('pole.kd', 100.0),
            ('pole.integral_limit', 0.5),
            ('cart.kp', 0.2),
            ('cart.ki', 0.0),
            ('cart.kd', 0.2),
            ('cart.integral_limit', 1.0),
            ('cart.max_pole_reference', 0.15),
        ])

        self.cart_joint = self.get_parameter('cart_joint').value
        self.pole_joint = self.get_parameter('pole_joint').value
        self.dt = 1.0 / self.get_parameter('rate').value

        self.pole_pid = PID()
        self.cart_pid = PID()
        self.load_gains()
        self.add_on_set_parameters_callback(self.on_set_parameters)
        self.add_post_set_parameters_callback(self.on_parameters_changed)

        # state
        self.x = self.x_dot = self.theta = self.theta_dot = 0.0
        self.has_state = False
        self.fallen = False

        self.cmd_pub = self.create_publisher(
            Float64MultiArray, self.get_parameter('command_topic').value, 10)
        self.create_subscription(JointState, '/joint_states', self.joint_state_callback, 10)
        self.create_subscription(Float64, '~/cart_setpoint', self.setpoint_callback, 10)
        self.create_timer(self.dt, self.control_loop)

        self.get_logger().info(
            f'PID controller aktif: {self.cart_joint} (effort) / {self.pole_joint} (pasif), '
            f'{1.0 / self.dt:.0f} Hz')

    # ------------------------------------------------------------------ params
    def load_gains(self):
        def p(name):
            return self.get_parameter(name).value

        self.max_effort = p('max_effort')
        self.fall_angle = p('fall_angle')
        self.cart_setpoint = p('cart_setpoint')

        self.pole_pid.kp = p('pole.kp')
        self.pole_pid.ki = p('pole.ki')
        self.pole_pid.kd = p('pole.kd')
        self.pole_pid.integral_limit = p('pole.integral_limit')
        self.pole_pid.output_limit = self.max_effort

        self.cart_pid.kp = p('cart.kp')
        self.cart_pid.ki = p('cart.ki')
        self.cart_pid.kd = p('cart.kd')
        self.cart_pid.integral_limit = p('cart.integral_limit')
        self.cart_pid.output_limit = p('cart.max_pole_reference')

    def on_set_parameters(self, params):
        read_only = {'rate', 'cart_joint', 'pole_joint', 'command_topic'}
        for param in params:
            if param.name in read_only:
                return SetParametersResult(
                    successful=False, reason=f'{param.name} hanya bisa diatur saat start')
        return SetParametersResult(successful=True)

    def on_parameters_changed(self, params):
        self.load_gains()
        self.get_logger().info(
            'parameter diperbarui: ' + ', '.join(f'{p.name}={p.value}' for p in params))

    # --------------------------------------------------------------- callbacks
    def joint_state_callback(self, msg):
        try:
            i_cart = msg.name.index(self.cart_joint)
            i_pole = msg.name.index(self.pole_joint)
        except ValueError:
            return
        self.x = msg.position[i_cart]
        self.x_dot = msg.velocity[i_cart]
        self.theta = wrap_angle(msg.position[i_pole])
        self.theta_dot = msg.velocity[i_pole]
        self.has_state = True

    def setpoint_callback(self, msg):
        # disimpan sebagai parameter supaya topic dan `ros2 param set` selalu konsisten
        self.set_parameters([Parameter('cart_setpoint', value=float(msg.data))])

    # ----------------------------------------------------------------- control
    def control_loop(self):
        if not self.has_state:
            return

        if abs(self.theta) > self.fall_angle:
            if not self.fallen:
                self.get_logger().warn(
                    f'pole jatuh (theta={self.theta:.2f} rad), kontrol dihentikan')
                self.fallen = True
            self.pole_pid.reset()
            self.cart_pid.reset()
            self.publish_effort(0.0)
            return
        if self.fallen:
            self.get_logger().info('pole kembali dalam jangkauan, kontrol dilanjutkan')
            self.fallen = False

        # outer loop: posisi cart -> referensi sudut pole
        theta_ref = self.cart_pid.update(self.cart_setpoint - self.x, -self.x_dot, self.dt)

        # inner loop: sudut pole -> gaya cart
        effort = self.pole_pid.update(self.theta - theta_ref, self.theta_dot, self.dt)

        self.publish_effort(effort)
        self.get_logger().debug(
            f'x={self.x:+.3f} theta={self.theta:+.4f} theta_ref={theta_ref:+.4f} F={effort:+.2f}')

    def publish_effort(self, effort):
        self.cmd_pub.publish(Float64MultiArray(data=[float(effort)]))


def main(args=None):
    rclpy.init(args=args)
    node = PIDController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.publish_effort(0.0)
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
