from string_operations import rjust, center, stretch
from math import atan2, pi
from machine import sleep, Pin
from utime import ticks_ms, sleep_ms
import source_MPU6050
import source_BMP180
import deneyap

bmp180 = source_BMP180.BMP180()
bmp180.preheat()
bmp180.calibrate()
mpu6050 = source_MPU6050.MPU6050()
mpu6050.set_sensitivity("gyroscope", 2000)
mpu6050.preheat()
mpu6050.gyroscope.calibration.calibrate()
    
rad_to_deg = 180 / pi
dt = 0

if __name__ == "__main__":
    for repetition in range(100):
        bmp180.update()
        for iteration in range(10):
            initial = ticks_ms()
            mpu6050.accelerometer.update()
            mpu6050.accelerometer.inclination.update()
            mpu6050.gyroscope.update()
            mpu6050.gyroscope.inclination.update(dt)
            mpu6050.fusion.update()
            sleep_ms(50)
            final = ticks_ms()
            dt = (final - initial) / 1000
        print("|Basınç     : " + rjust(stretch(str(bmp180.pressure), target=2), target=8, key=" ") + "|")
        print("|İrtifa     : " + rjust(stretch(str(bmp180.altitude.current), target=2), target=8, key=" ") + "|")
        print("|Sıcaklık   : " + rjust(stretch(str(bmp180.temperature), target=2), target=8, key=" ") + "|")
        print("|Yunuslama  : " + rjust(stretch(str(mpu6050.accelerometer.inclination.roll), target=2), target=8, key=" ") + "|")
        print("|Yuvarlanma : " + rjust(stretch(str(mpu6050.accelerometer.inclination.pitch), target=2), target=8, key=" ") + "|")
        print("|" + ("-" * 21) + "|")

        

