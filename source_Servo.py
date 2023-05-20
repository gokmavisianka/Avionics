from math_operations import LineerInterpolation as lineer_interpolation
import machine
import deneyap
import utime


class Servo:
    def __init__(self, pin, frequency=50):
        # Yalnızca <frequency = 50> için test edilmiştir, bu değeri değiştirmeyiniz.
        self.motor = machine.PWM(machine.Pin(pin), frequency)
        
    def rotate(self, degree):
        # Lineer interpolasyon uygulanarak, açı değeri frekansa göre ayarlanır.
        if -90 <= degree <= 90:
            value = lineer_interpolation.servo(degree)
            self.motor.duty(value)
        else:
            raise ValueError("Can only rotate between -90 and 90 degrees!")
  
  
if __name__ == "__main__":
    # Test
    servo = Servo(deneyap.D12)
    servo.rotate(0)
    utime.sleep(2)
    servo.rotate(180)
