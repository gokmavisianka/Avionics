from machine import I2C, Pin
import source_MPU6050
import source_BMP180
import deneyap

class Sensors:
    def __init__(self):
        self.i2c = I2C(scl=Pin(deneyap.SCL), sda=Pin(deneyap.SDA))
        self.bmp180 = self.BMP180(self.i2c)
        self.mpu6050 = self.MPU6050(self.i2c)
            
    class BMP180:
        def __init__(self, i2c):
            self.sensor = source_BMP180.Sensor(i2c)
            self.temperature = 0
            self.pressure = 0
            self.altitude = 0
            self.values = {}
            
        def update(self):
            self.values = self.sensor.get_values()
            self.temperature = values["temperature"]
            self.pressure = self.values["pressure"]
            self.altitude = self.values["altitude"]
        
        def read(self, form="string"):
                if form == "string":
                    return "{0}:{1}:{2}".format(self.temperature, self.pressure, self.altitude)
                elif form == "dictionary":
                    return self.values
                else:
                    raise ValueError("Unexpected argument for parameter 'form'!")
            
    class MPU6050:
        def __init__(self, i2c):
            self.sensor = source_MPU6050.Sensor(i2c)
            self.gyroscope = self.Gyroscope(self.sensor)
            self.accelerometer = self.Accelerometer(self.sensor)
            
        class Gyroscope:
            def __init__(self, sensor):
                self.x = self.y = self.z = 0
                self.sensor = sensor
                self.values = {}
                
            def update(self):
                self.values = self.sensor.get_values("gyroscope")
                self.x = self.values["gyroscope"]["x"]
                self.y = self.values["gyroscope"]["x"]
                self.z = self.values["gyroscope"]["x"]
                
            def read(self, form="string"):
                if form == "string":
                    return "{0}:{1}:{2}".format(self.x, self.y, self.z)
                elif form == "dictionary":
                    return self.values
                else:
                    raise ValueError("Unexpected argument for parameter 'form'!")
                
        class Accelerometer:
            def __init__(self, sensor):
                self.x = self.y = self.z = 0
                self.sensor = sensor
                self.values = {}
                
            def update(self):
                self.values = self.sensor.get_values("accelerometer")
                self.x = self.values["accelerometer"]["x"]
                self.y = self.values["accelerometer"]["y"]
                self.z = self.values["accelerometer"]["z"]
                
            def read(self, form="string"):
                if form == "string":
                    return "{0}:{1}:{2}".format(self.x, self.y, self.z)
                elif form == "dictionary":
                    return self.values
                else:
                    raise ValueError("Unexpected argument for parameter 'form'!")
            