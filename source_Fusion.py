# This file is not in use.
# Please check the source_MPU6050.py file to see how the "Sensor Fusion" is applied.

class Fusion:
    def __init__(self, sensors):
        self.sensors = sensors
        self.yaw = self.roll = self.pitch = 0
        self.alpha = 0.90
        
    def update(self):
        gyroscope = self.sensors.MPU6050.gyroscope
        accelerometer = self.sensors.MPU6050.accelerometer
        self.roll = (self.roll + gyroscope.angle.roll) * self.alpha + (acceleration.angle.roll) * (1 - self.alpha)
        self.pitch = (self.pitch + gyroscope.angle.pitch) * self.alpha + (acceleration.angle.pitch) * (1 - self.alpha)
            
