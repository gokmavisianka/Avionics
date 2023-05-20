from machine import I2C, Pin, sleep
from string_operations import rjust, stretch
from ustruct import unpack
import deneyap
import utime
import math

# BMP180 class
class BMP180():
    def __init__(self, i2c=I2C(scl=Pin(deneyap.SCL), sda=Pin(deneyap.SDA)), address=119):
        self.altitude = self.Altitude()
        self.temperature = 0
        self.pressure = 0
        self.address = address
        self.connection = i2c
        self.connection.start()
        self.chip_id = self.read_from_memory('_', 0xD0, 2, do_unpack=False)
        # Kalibrasyon katsayıları (Her biri 16 bitten oluşan 11 katsayı).
        self.variable_coefficients = {"temperature": {"AC5": self.read_from_memory('>H', 0xB2, 2)[0],
                                                      "AC6": self.read_from_memory('>H', 0xB4, 2)[0],
                                                      "MC" : self.read_from_memory('>h', 0xBC, 2)[0],
                                                      "MD" : self.read_from_memory('>h', 0xBE, 2)[0]},
                                      "pressure"   : {"AC1": self.read_from_memory('>h', 0xAA, 2)[0],
                                                      "AC2": self.read_from_memory('>h', 0xAC, 2)[0],
                                                      "AC3": self.read_from_memory('>h', 0xAE, 2)[0],
                                                      "AC4": self.read_from_memory('>H', 0xB0, 2)[0],
                                                      "B1" : self.read_from_memory('>h', 0xB6, 2)[0],
                                                      "B2" : self.read_from_memory('>h', 0xB0, 2)[0],
                                                      "MB" : self.read_from_memory('>h', 0xBA, 2)[0]}}
        
        # 'sensitivity' ayarı. 0, 1, 2 veya 3 olmalıdır. Değer arttıkça doğruluk oranı artar ama okuma süresi de uzar.
        self.oversample_setting = 3
        
        # Deniz seviyesindeki basınç değeri, 101325 Pascal.
        self.baseline = 101325.0
        
        # Sensörden okunan asıl 'raw' değerler.
        self.raw = {"UT": None, "B5": None, "MSB": None, "LSB": None, "XLSB": None}
    
    # Sensörün belleğinden veri okuma.
    def read_from_memory(self, symbol='>h', target=0x00, length=1, do_unpack=True) -> int:
        if do_unpack is True:
            return unpack(symbol, self.connection.readfrom_mem(self.address, target, length))
        else:
            return self.connection.readfrom_mem(self.address, target, length)
        
    # Sensörün belleğine veri kaydetme.
    def write_to_memory(self, target=0x00, data: list=[]) -> None:
        self.connection.writeto_mem(self.address, target, bytearray(data))
    
    # Sensörden verileri okuduğumuz fonksiyon.
    def read(self) -> None:
        # delays, oversample ayarına göre verilerin hazır olması için beklenecek süreleri belirtir.
        delays = (5, 8, 14, 25)
        self.write_to_memory(0xF4, [0x2E])
        # Sıcaklık için gerekli olan veri hazır oluncaya dek bekle.
        utime.sleep_ms(5)
        try:
            # Sıcaklık için gerekli veriyi okumaya çalış.
            self.raw["UT"] = self.read_from_memory('_', 0xF6, 2, do_unpack=False)
        except:
            pass
        self.write_to_memory(0xF4, [0x34 + (self.oversample_setting << 6)])
        # Basınç için gerekli olan veriler hazır oluncaya dek bekle.
        utime.sleep_ms(delays[self.oversample_setting])
        try:
            # Basınç için gerekli verileri okumaya çalış.
            self.raw["MSB"] = self.read_from_memory('_', 0xF6, 1, do_unpack=False)
            self.raw["LSB"] = self.read_from_memory('_', 0xF7, 1, do_unpack=False)
            self.raw["XLSB"] = self.read_from_memory('_', 0xF8, 1, do_unpack=False)
        except:
            pass
    
    # Verileri işleyerek sıcaklık değerini elde ettiğimiz fonksiyon.
    def get_temperature(self) -> float:
        temperature = self.variable_coefficients["temperature"]
        try:
            UT = unpack('>H', self.raw["UT"])[0]
        except:
            return 0.0
        X1 = (UT - temperature["AC6"]) * temperature["AC5"] / (2 ** 15)
        X2 = temperature["MC"] * (2 ** 11) / (X1 + temperature["MD"])
        self.raw["B5"] = X1 + X2
        value = (((X1 + X2) + 8) / (2 ** 4)) / 10
        return round(value, 2)
    
    # Verileri işleyerek basınç değerini elde ettiğimiz fonksiyon.
    def get_pressure(self) -> float:
        pressure = self.variable_coefficients["pressure"]
        try:
            MSB = unpack('B', self.raw["MSB"])[0]
            LSB = unpack('B', self.raw["LSB"])[0]
            XLSB = unpack('B', self.raw["XLSB"])[0]
        except:
            return 0.0
        
        U = ((MSB << 16) + (LSB << 8) + XLSB) >> (8 - self.oversample_setting)
        A = self.raw["B5"] - 4000
        V = (pressure["B2"] * ((A ** 2) / (2 ** 12)) + pressure["AC2"] * A) / (2 ** 11)
        B = ((int((pressure["AC1"] * 4 + V)) << self.oversample_setting) + 2) / 4
        V = 0.5 + (8 * pressure["AC3"] * A + pressure["B1"] * ((A ** 2) / (2 ** 12))) / (2 ** 16) / 4
        C = abs(pressure["AC4"]) * (V + 2 ** 15) / (2 ** 15)
        D = (abs(U) - B) * (50000 >> self.oversample_setting)
        
        P = 2 * (D / C)
        value = P + (3791 + (P * (3038 * P - 7357 * 2 ** 16)) / (2 ** 32)) / 16
        return round(value, 2)
    
    # Verileri işleyerek irtifa değerini elde ettiğimiz fonksiyon.
    def get_altitude(self) -> float:
        try:
            altitude = -7990.0 * math.log(self.pressure / self.baseline)
        except:
            altitude = 0.0
        return round(altitude, 2)
    
    # preheat.
    def preheat(self, count: int=10, delay: int=5) -> None:
        for number in range(count):
            self.update()
            utime.sleep_ms(delay)
        
    # Kalibrasyon.
    def calibrate(self, count: int=10, delay: int=5) -> None:
        summation = 0
        for number in range(count):
            self.update()
            summation += self.altitude.current
            utime.sleep_ms(delay)
        average = summation / count
        self.altitude.initial = average
            
    # Verileri güncellediğiniz fonksiyon.
    def update(self) -> None:
        self.read()
        self.temperature = self.get_temperature()
        self.pressure = self.get_pressure()
        self.altitude.current = round(self.get_altitude(), 2)
        self.altitude.difference = round(self.altitude.current - self.altitude.initial, 2)
        
    # İrtifa değeri için oluşturulan sınıf.
    class Altitude:
        def __init__(self):
            self.initial = self.current = 0
            self.difference = 0

if __name__ == "__main__":
    bmp180 = BMP180()
    for _ in range(100):
        bmp180.update()
        print("|Basınç    :", rjust(stretch(str(bmp180.pressure), target=2), target=8, key=" ") + "|")
        print("|İrtifa    :", rjust(stretch(str(bmp180.altitude.current), target=2), target=8, key=" ") + "|")
        print("|Sıcaklık  :", rjust(stretch(str(bmp180.temperature), target=2), target=8, key=" ") + "|")
        print("|" + ("-" * 20) + "|")
        utime.sleep_ms(100)
    print("Bitti!")
    

