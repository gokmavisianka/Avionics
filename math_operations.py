# Birden çok dosyada ihtiyaç duyulan bazı matematiksel fonksiyonların yer aldığı dosya.

# lineer interpolasyon için oluşturulan bir sınıf.
class LineerInterpolation:
    @staticmethod
    def evaluate(x1, x2, y1, y2, current):
        return round((((current - x1) * (y2 - y1)) / (x2 - x1) + y1), 2)
    
    @classmethod
    def acceleration(self, value, sensitivity=1):
        x = 32768
        y = 19.6 * sensitivity
        return self.evaluate(-x, x, -y, y, value)
    
    @classmethod
    def gyroscope(self, value, sensitivity=1):
        x = 32768
        y = 250 * sensitivity
        return self.evaluate(-x, x, -y, y, value)
    
    @classmethod
    def servo(self, value, frequency=50):
        x1, x2 = -90, 90
        y1, y2 = 25, 130  # <frequency = 50> için ayarlanmıştır.
        return self.evaluate(x1, x2, y1, y2, value)

# Açı değerini 0 ila 360 arasında tutmak için kullanılan fonksiyon.
# match_the_range(-10) -> 350, match_the_range(370) -> 10 gibi...
def match_the_range(value):
    while value < 0:
        value = value + 360
    while value > 360:
        value = value - 360
    return value

# Bir sayının basamak sayısını elde etmek için kullanılan fonksiyon.
def length(number):
    try:
        return len(str(int(number)))
    except ValueError:
        print("Warning: length(value), type of <value> should be <integer or float> but {0} is taken.".format(type(value)))
        return 0
        xz