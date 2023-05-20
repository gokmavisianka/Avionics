# zaman verisini elde etmek için kullandığımız dosya (bataryadan beslenen bir kart için denenmedi).

from time import localtime
from string_operations import rjust


class Time:
    def read(self):
        data = localtime()[3:6]
        hour = rjust(string=str(data[0]), target=2, key="0")
        minute = rjust(string=str(data[1]), target=2, key="0")
        second = rjust(string=str(data[2]), target=2, key="0")
        return hour + "." + minute + "." + second
    