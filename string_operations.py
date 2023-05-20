# Verilerin okunmasını kolaylaştırmak adına yazılan bazı fonksiyonları barındıran dosya.

# Yazının sol tarafına istenen bir karakteri istenen sayıda yerleştirir.
def rjust(string, target, key=" "):
    length = len(string)
    difference = target - length
    if difference > 0:
        gap = difference * key
        return gap + string
    elif difference == 0:
        return string
    else:
        return string[:target]
    
# Yazıyı ortalamak için hem soluna hem de sağına istenen bir karakteri ekler.
def center(string, target, key=" "):
    length = len(string)
    difference = target - length
    if difference == 0:
        return string
    elif difference < 0:
        return string[:target]
    elif difference % 2 == 0:
        gap = key * (difference // 2)
        return gap + string + gap
    else:
        value = difference // 2
        gap = key * value
        if value == 0:
            return key + string
        else:
            return key + gap + string + gap
        
def stretch(string, target):
    if type(string) == str:
        elements = string.split(".")
        count = len(elements)
        if count == 2:
            left, right = elements
            length = len(right)
            if length < target:
                difference = target - length
                gap = "0" * difference
                right = right + gap
            elif length > target:
                right = right[:target]
        elif count == 1:
            left = string
            right = "0" * target
        else:
            left = "0"
            right = "0" * target
        string = "{0}.{1}".format(left, right)
        return string
    else:
        return "0." + ("0" * target)