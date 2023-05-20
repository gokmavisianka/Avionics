class Fusion:
    def __init__(self, sensors):
        self.sensors = sensors
        self.yaw = self.roll = self.pitch = 0
        self.alpha = 0.90
        
    def update(self, case=0):
        gyroscope = sensors.MPU6050.gyroscope
        accelerometer = sensors.MPU6050.accelerometer
        if case == 2:
            self.roll = (self.roll + gyroscope.angle.roll) * self.alpha + (acceleration.angle.roll) * (1 - self.alpha)
            self.pitch = (self.pitch + gyroscope.angle.pitch) * self.alpha + (acceleration.angle.pitch) * (1 - self.alpha)
            
