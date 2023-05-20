from string_operations import rjust, stretch
from machine import I2C, Pin
from math_operations import LineerInterpolation as lineer_interpolation
from math_operations import match_the_range
from math import atan2, pi
from utime import sleep_ms, ticks_ms
import deneyap
import machine

# math_operations.py isimli dosyadan aktarılan lineer interpolasyon fonksiyonu
# radyanı dereceye çevirmek için kullandığımız sayısal değer.
rad_to_deg = 180 / pi

# MPU6050 sınıfı
class MPU6050():
    def __init__(self, i2c=I2C(scl=Pin(deneyap.SCL), sda=Pin(deneyap.SDA)), address=0x68):
        self.address = address
        self.connection = i2c
        self.connection.start()
        self.connection.writeto(self.address, bytearray([107, 0]))
        self.connection.stop()
        self.fusion = self.Fusion(self)
        self.gyroscope = self.Gyroscope(self)
        self.accelerometer = self.Accelerometer(self)
        self.sensitivity = {"gyroscope": 1, "accelerometer": 1}
    
    # 'sensitivity' değerinin ayarlandığı fonksiyon.
    def set_sensitivity(self, part=None, value=None, GYRO_CONFIG=0x1b, ACCEL_CONFIG=0x1c):
        FS_SEL = {250: 0, 500: 1, 1000: 2, 2000: 3}
        AFS_SEL = {"2g": 0, "4g": 1, "8g": 2, "16g": 3}
        if part == "gyroscope":
            if value in FS_SEL:
                self.connection.start()
                self.connection.writeto_mem(self.address, GYRO_CONFIG, bytes([FS_SEL[value]]))
                self.connection.stop()
                self.sensitivity["gyroscope"] = 2 ** FS_SEL[value]
            else:
                print("Warning: set_sensitivity(part={0}, value={1})".format(part, value))
                print("the argument for <value> must be in (250, 500, 1000, 2000), type=<class 'int'>")
                print("<250> is passed as default value -> FS_SEL = 0")
                self.set_sensitivity(part, 250) 
        elif part == "accelerometer":
            if value in AFS_SEL:
                self.connection.start()
                self.connection.writeto_mem(self.address, ACCEL_CONFIG, bytes([AFS_SEL[value]]))
                self.connection.stop()
                self.sensitivity["accelerometer"] = 2 ** AFS_SEL[value]
            else:
                print("Warning: set_sensitivity(part={0}, value={1})".format(part, value))
                print("the argument for <value> must be in ('2g', '4g', '8g', '16g'), type=<class 'str'>")
                print("<'2g'> is passed as default value -> AFS_SEL = 0")
                self.set_sensitivity(part, "2g")     
        else:
            print("Warning: set_sensitivity(part={0}, value={1})".format(part, value))
            print("the argument for <part> must be in ('gyroscope', 'accelerometer'), type=<class 'str'>")
            if value in FS_SEL:
                part = "gyroscope"
            elif value in AFS_SEL:
                part = "accelerometer"
            else:
                part = None
            if part is not None:
                print("<part={0}> is passed according to the <value={1}>".format(part, value))
                self.set_sensitivity(part, value)
            else:
                print("Function skipped due to wrong argument(s).")
         
    # İngilizcesini 'preheat' olarak sallamış olduğum fonksiyon.
    # Fonksiyonun amacı, sensöre güç verildiğinde bir miktar okuma yapmak.
    def preheat(self, count=10, delay=10):
        for number in range(count):
            self.accelerometer.update()
            self.gyroscope.update(calibrated=False)
            self.accelerometer.inclination.update()
            sleep_ms(delay)
        # Roket harekete geçmeden önce, jiroskopun açı değerlerini, ivmeölçerden elde edilen açı değerleri ile güncelleyelim.
        self.gyroscope.inclination.roll = self.accelerometer.inclination.roll
        self.gyroscope.inclination.pitch = self.accelerometer.inclination.pitch
        self.fusion.roll = self.accelerometer.inclination.roll
        self.fusion.pitch = self.accelerometer.inclination.pitch
    
    # Sensörün 0x3B adresinden verileri okuduğumuz fonksiyon.
    def get_raw_values(self):
        self.connection.start()
        raw_values = self.connection.readfrom_mem(self.address, 0x3B, 14)
        self.connection.stop()
        return raw_values
    
    def get_ints(self):
        raw_values = self.get_raw_values()
        raw_ints = []
        for value in raw_values:
            raw_ints.append(value)
        return raw_ints
    
    def bytes_to_int(self, first_byte, second_byte):
        if not first_byte & 0x80:
            return first_byte << 8 | second_byte
        return - (((first_byte ^ 255) << 8) | (second_byte ^ 255) + 1)
    
    # Sensörlerden okumaların yapıldığı ve okunan değerlerin mevcut 'sensitivity' değerine göre yorumlandığı fonksiyon.
    # Sensörlerden gelen veriler 2^(-14) ila 2^(14) arasında bir değer olur.
    # Bu değeri bizim sensitivity değerine göre tam sayıya çevirmemiz gerekir. Bunun için de lineer interpolasyon kullanırız.
    # Örneğin sensitivity değeri bize aralığın -100 ila 100 olduğunu belirtiyorsa, 2^(-14) = -100 ve 2^(14) = 100 olacaktır.
    def get_values(self, sensor):
        raw_ints = self.get_raw_values()
        data = {"x": 0, "y": 0, "z": 0}
        if sensor == "accelerometer":
            sensitivity = self.sensitivity["accelerometer"]
            data["x"] = lineer_interpolation.acceleration(self.bytes_to_int(raw_ints[0], raw_ints[1]), sensitivity)
            data["y"] = lineer_interpolation.acceleration(self.bytes_to_int(raw_ints[2], raw_ints[3]), sensitivity)
            data["z"] = lineer_interpolation.acceleration(self.bytes_to_int(raw_ints[4], raw_ints[5]), sensitivity)
        elif sensor == "gyroscope":
            data["x"] = lineer_interpolation.gyroscope(self.bytes_to_int(raw_ints[8], raw_ints[9]))
            data["y"] = lineer_interpolation.gyroscope(self.bytes_to_int(raw_ints[10], raw_ints[11]))
            data["z"] = lineer_interpolation.gyroscope(self.bytes_to_int(raw_ints[12], raw_ints[13]))
        else:
            print("Warning: get_values(sensor={0})".format(sensor))
            print("the argument for <sensor> must be in ('gyroscope', 'accelerometer'), type=<class 'str'>")
            print("Function skipped due to wrong argument.")
        return data
    
    # İvmeölçerden ve jiroskoptan alınan verilerin birleştirilerek filtreden geçirildiği sınıf.
    class Fusion:
        def __init__(self, sensor):
            self.roll = self.pitch = self.yaw = 0
            self.sensor = sensor
            self.alpha = 0.96
        
        # roll ve pitch değerlerinin tamamlayıcı (complementary) filtreden geçirilerek güncellendiği fonksiyon.
        def update(self):
            # A_r = ivmeölçerden elde edilen 'roll' değeri
            # G_r = Jiroskoptan  elde edilen 'roll' değeri
            A_r = self.sensor.accelerometer.inclination.roll
            G_r = (self.roll + self.sensor.gyroscope.inclination.roll - self.sensor.gyroscope.inclination.previous.roll)
            if (A_r > 300 and G_r < 100):
                self.roll = match_the_range(self.alpha * G_r + (1 - self.alpha) * (A_r - 360))
            elif (G_r > 300 and A_r < 100):
                self.roll = match_the_range(self.alpha * (G_r - 360) + (1 - self.alpha) * A_r)
            else:
                self.roll = match_the_range(self.alpha * G_r + (1 - self.alpha) * A_r)
            
            # A_p = ivmeölçerden elde edilen 'pitch' değeri
            # G_p = Jiroskoptan  elde edilen 'pitch' değeri
            A_p = self.sensor.accelerometer.inclination.pitch
            G_p = (self.pitch + self.sensor.gyroscope.inclination.pitch - self.sensor.gyroscope.inclination.previous.pitch)
            if (A_p > 300 and G_p < 100):
                self.pitch = match_the_range(self.alpha * G_p + (1 - self.alpha) * (A_p - 360))
            elif (G_p > 300 and A_p < 100):
                self.pitch = match_the_range(self.alpha * (G_p - 360) + (1 - self.alpha) * A_p)
            else:
                self.pitch = match_the_range(self.alpha * G_p + (1 - self.alpha) * A_p)

    # Jiroskop sınıfı  
    class Gyroscope:
        def __init__(self, sensor):
            self.sensor = sensor
            self.calibration = self.Calibration(self)
            self.inclination = self.Inclination(self)
            self.x = self.y = self.z = 0
            self.values = {}
           
        # 3 eksendeki açısal hız değerlerinin güncellendiği fonksiyon.
        def update(self, calibrated=True):
            self.values = self.sensor.get_values("gyroscope")
            self.x = self.values["x"]
            self.y = self.values["y"]
            self.z = self.values["z"]
            if calibrated:
                self.x = self.calibration.filtrate("x", self.x)
                self.y = self.calibration.filtrate("y", self.y)
                self.z = self.calibration.filtrate("z", self.z)
            
        # Kalibrasyon sınıfı   
        class Calibration:
            def __init__(self, sensor):
                self.x, self.y, self.z = [], [], []
                self.sensor = sensor
                self.interval = {"x": {"left": 0, "right": 0},
                                 "y": {"left": 0, "right": 0},
                                 "z": {"left": 0, "right": 0}}
                self.noise = {"x": 0, "y": 0, "z": 0}
            
            # <interval> milisaniye boyunca <count> okuma yapılarak veriler listelere aktarılır.
            def calibrate(self, count=100, interval=1000):
                delay = interval / count
                for _ in range(count):
                    self.sensor.update(calibrated=False)
                    self.x.append(self.sensor.x)
                    self.y.append(self.sensor.y)
                    self.z.append(self.sensor.z)
                    sleep_ms(int(delay))
                self.update(count)
            
            # gürültü (noise) ve 'gürültüsüz minimum ve maksimum değer aralığı' verilerinin güncellendiği fonksiyon.
            def update(self, NoE):
                self.noise["x"] = sum(self.x) / NoE
                self.noise["y"] = sum(self.y) / NoE
                self.noise["z"] = sum(self.z) / NoE
                self.interval["x"]["left"] = min(self.x) - self.noise["x"]
                self.interval["x"]["right"] = max(self.x) - self.noise["x"]
                self.interval["y"]["left"] = min(self.y) - self.noise["y"]
                self.interval["y"]["right"] = max(self.y) - self.noise["y"]
                self.interval["z"]["left"] = min(self.z) - self.noise["z"]
                self.interval["z"]["right"] = max(self.z) - self.noise["z"]
            
            # Herhangi bir eksendeki güncel açısal hız değerinin, minimum ve maksimum değer arasında olması durumunda bu değer 0 ile değiştirilir.
            # Buradaki amaç, ufak miktarlardaki engellenemeyen 'gürültü'lerin önüne geçmektir (uzun vadede sapmaya neden olabilir).
            def filtrate(self, axis, initial):
                last = initial - self.noise[axis]
                if self.interval[axis]["left"] < last < self.interval[axis]["right"]:
                    return 0
                else:
                    return last
                
        # Eğim sınıfı      
        class Inclination:
            def __init__(self, sensor):
                self.previous = self.Previous()
                self.sensor = sensor
                self.pitch = 0
                self.roll = 0
                self.yaw = 0
                
            # açıdaki değişim = açısal hız * geçen zaman
            # güncel açı = önceki açı + açıdaki değişim
            # 3 eksendeki açı değerlerinin elde edildiği fonksiyon.
            def update(self, dt):
                self.previous.roll = self.roll
                self.previous.pitch = self.pitch
                self.previous.yaw = self.yaw
                self.roll = match_the_range((self.roll + self.sensor.x * dt))
                self.pitch = match_the_range((self.pitch + self.sensor.y * dt))
                self.yaw = match_the_range((self.yaw + self.sensor.z * dt))
                
            # Önceki açı değerlerinin saklandığı sınıf
            class Previous:
                def __init__(self):
                    self.pitch = 0
                    self.roll = 0
                    self.yaw = 0
    
    # İvmeölçer sınıfı
    class Accelerometer:
        def __init__(self, sensor):
            self.inclination = self.Inclination(self)
            self.x = self.y = self.z = 0
            self.sensor = sensor
            self.values = {}
        
        # 3 eksendeki ivme değerlerini ölçer.
        def update(self):
            self.values = self.sensor.get_values("accelerometer")
            self.x = self.values["x"]
            self.y = self.values["y"]
            self.z = self.values["z"]
        
        # Eğim sınıfı
        class Inclination:
            def __init__(self, sensor):
                self.sensor = sensor
                self.pitch = 0
                self.roll = 0
                self.yaw = 0
            
            # Yerçekimi ivmesi referans alınarak, 3 eksendeki ivme değerleri ile yine bu 3 eksendeki eğim/açı hesaplanabilir.
            # Hesaplamalar, sensöre yalnızca yerçekimi ivmesinin etki ettiği anda ~%100 güvenilirdir.
            # Dışarıdan etki eden herhangi bir kuvvet, bu açıların doğruluğunu etkileyecektir.
            # Bu yüzden, buradaki verilerin ancak roketin yakıtı bittikten sonra veya roket havalanmadan önce kullanılması çok daha doğru olacaktır.
            # Neyse ki, roketin hızı azaldıkça ona etki eden sürtünme kuvvetinin büyüklüğü de azalacaktır.
            # Buna bağlı olarak, tepe noktasına yaklaşıldıkça buradan elde edilen verilerin güvenilirliği artacaktır.      
            # Trigonometrideki arctan fonksiyonunun 4 kadranlı versiyonu kullanılır.
            # Normal şartlarda arctan fonksiyonu bizlere -90 ila 90 arasında bir derece verir.
            # Fakat 4 kadranlı arctan fonksiyonu bu aralığı -180 ila 180 olarak genişletir.
            def update(self):
                self.roll = round(rad_to_deg * (pi + atan2(-self.sensor.y, -self.sensor.z)), 2)
                self.pitch = round(rad_to_deg * (pi + atan2(-self.sensor.x, -self.sensor.z)), 2)
                self.yaw = round(rad_to_deg * (pi + atan2(-self.sensor.y, -self.sensor.x)), 2)
            

if __name__ == "__main__":
    mpu6050 = MPU6050()
    mpu6050.preheat()
    mpu6050.gyroscope.calibration.calibrate()
    dt = 0
    for repetition in range(100):
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
        print("|Yunuslama  : " + rjust(stretch(str(mpu6050.fusion.roll), target=2), target=6, key=" ") + "|")
        print("|Yuvarlanma : " + rjust(stretch(str(mpu6050.fusion.pitch), target=2), target=6, key=" ") + "|")
        print("|" + ("-" * 19) + "|")
        
