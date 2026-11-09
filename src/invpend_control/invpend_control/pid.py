"""PID sederhana dengan anti-windup dan saturasi output."""


def clamp(value, low, high):
    return max(low, min(high, value))


class PID:
    """
    Output = kp * error + ki * integral(error) + kd * error_rate.

    error_rate diberikan dari luar (misal dari kecepatan joint) supaya tidak
    perlu menurunkan sinyal secara numerik yang rentan noise.
    """

    def __init__(self, kp=0.0, ki=0.0, kd=0.0, output_limit=float('inf'),
                 integral_limit=float('inf')):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limit = output_limit
        self.integral_limit = integral_limit
        self.integral = 0.0

    def reset(self):
        self.integral = 0.0

    def update(self, error, error_rate, dt):
        self.integral = clamp(
            self.integral + error * dt, -self.integral_limit, self.integral_limit)
        output = self.kp * error + self.ki * self.integral + self.kd * error_rate
        return clamp(output, -self.output_limit, self.output_limit)
